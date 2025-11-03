"""Authentication module for TMI OAuth flow."""

import json
import logging
import webbrowser
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

import requests

from tmi_tf.config import Config

logger = logging.getLogger(__name__)


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""

    authorization_code: Optional[str] = None
    state: Optional[str] = None

    def do_GET(self):
        """Handle GET request for OAuth callback."""
        # Parse query parameters
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        # Extract authorization code and state
        OAuthCallbackHandler.authorization_code = params.get("code", [None])[0]
        OAuthCallbackHandler.state = params.get("state", [None])[0]

        # Send response
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if OAuthCallbackHandler.authorization_code:
            self.wfile.write(
                b"<html><body><h1>Authentication successful!</h1>"
                b"<p>You can close this window and return to the terminal.</p>"
                b"</body></html>"
            )
        else:
            self.wfile.write(
                b"<html><body><h1>Authentication failed!</h1>"
                b"<p>No authorization code received.</p>"
                b"</body></html>"
            )

    def log_message(self, format, *args):
        """Suppress HTTP server logs."""
        pass


class TokenCache:
    """Manages JWT token caching."""

    def __init__(self, cache_file: Path):
        """Initialize token cache."""
        self.cache_file = cache_file

    def save_token(self, token: str, expires_in: int):
        """Save token to cache file."""
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        cache_data = {"token": token, "expires_at": expires_at.isoformat()}

        with open(self.cache_file, "w") as f:
            json.dump(cache_data, f)

        logger.info(f"Token cached to {self.cache_file}")

    def load_token(self) -> Optional[str]:
        """Load token from cache if valid."""
        if not self.cache_file.exists():
            return None

        try:
            with open(self.cache_file, "r") as f:
                cache_data = json.load(f)

            expires_at = datetime.fromisoformat(cache_data["expires_at"])
            if datetime.now() < expires_at:
                logger.info("Using cached token")
                return cache_data["token"]
            else:
                logger.info("Cached token expired")
                return None
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to load cached token: {e}")
            return None

    def clear_token(self):
        """Clear cached token."""
        if self.cache_file.exists():
            self.cache_file.unlink()
            logger.info("Token cache cleared")


class TMIAuthenticator:
    """Handles OAuth authentication with TMI server."""

    def __init__(self, config: Config):
        """Initialize authenticator."""
        self.config = config
        self.token_cache = TokenCache(config.token_cache_file)
        self.callback_port = 8888
        self.redirect_uri = f"http://localhost:{self.callback_port}/callback"

    def get_token(self, force_refresh: bool = False) -> str:
        """
        Get authentication token (from cache or by performing OAuth flow).

        Args:
            force_refresh: Force new authentication even if cached token exists

        Returns:
            JWT access token
        """
        if not force_refresh:
            cached_token = self.token_cache.load_token()
            if cached_token:
                return cached_token

        logger.info("Starting OAuth authentication flow")
        return self._perform_oauth_flow()

    def _perform_oauth_flow(self) -> str:
        """
        Perform OAuth 2.0 authorization code flow.

        Returns:
            JWT access token
        """
        # Step 1: Get authorization URL
        auth_url = self._get_authorization_url()
        logger.info(f"Opening browser for authentication: {auth_url}")

        # Open browser
        webbrowser.open(auth_url)

        # Step 2: Start local server to receive callback
        authorization_code = self._wait_for_callback()

        if not authorization_code:
            raise RuntimeError("Failed to receive authorization code from callback")

        # Step 3: Exchange authorization code for token
        token = self._exchange_code_for_token(authorization_code)

        return token

    def _get_authorization_url(self) -> str:
        """
        Get OAuth authorization URL from TMI server.

        Returns:
            Authorization URL to open in browser
        """
        url = f"{self.config.tmi_server_url}/api/oauth/authorize"
        params = {
            "idp": self.config.tmi_oauth_idp,
            "client_callback": self.redirect_uri,
            "scope": "openid profile email",
        }

        try:
            response = requests.get(url, params=params, allow_redirects=False)
            response.raise_for_status()

            # TMI server should redirect to Google OAuth
            if response.status_code == 302:
                return response.headers["Location"]
            else:
                # Or return the authorization URL directly
                return response.json().get("authorization_url", response.url)

        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get authorization URL: {e}")

    def _wait_for_callback(self) -> Optional[str]:
        """
        Start local HTTP server and wait for OAuth callback.

        Returns:
            Authorization code from callback
        """
        # Reset class variables
        OAuthCallbackHandler.authorization_code = None
        OAuthCallbackHandler.state = None

        # Start server
        server = HTTPServer(("localhost", self.callback_port), OAuthCallbackHandler)
        logger.info(f"Waiting for OAuth callback on port {self.callback_port}...")

        # Handle one request (the callback)
        server.handle_request()

        return OAuthCallbackHandler.authorization_code

    def _exchange_code_for_token(self, authorization_code: str) -> str:
        """
        Exchange authorization code for JWT token.

        Args:
            authorization_code: OAuth authorization code

        Returns:
            JWT access token
        """
        url = f"{self.config.tmi_server_url}/api/oauth/exchange"

        # Note: The TMI API might expect different payload format
        # This is based on typical OAuth flows - may need adjustment
        data = {
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
        }

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()

            token_data = response.json()
            access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)

            if not access_token:
                raise RuntimeError("No access_token in response")

            # Cache the token
            self.token_cache.save_token(access_token, expires_in)

            logger.info("Successfully obtained access token")
            return access_token

        except requests.RequestException as e:
            raise RuntimeError(f"Failed to exchange code for token: {e}")

    def clear_cached_token(self):
        """Clear cached authentication token."""
        self.token_cache.clear_token()
