"""
Ngrok Tunnel Integration

Provides functionality to create public tunnel for local server.
"""

from typing import Optional

from src.config import get_config
from src.logger import get_logger

logger = get_logger(__name__)


class NgrokTunnel:
    """Manages ngrok tunnel for public access."""

    def __init__(self):
        self.config = get_config()
        self._tunnel = None
        self._public_url: Optional[str] = None

    @property
    def is_enabled(self) -> bool:
        """Check if ngrok is enabled in config."""
        return self.config.ngrok.enabled

    @property
    def public_url(self) -> Optional[str]:
        """Get the public URL if tunnel is active."""
        return self._public_url

    def start(self, port: int) -> Optional[str]:
        """
        Start ngrok tunnel.

        Args:
            port: Local port to tunnel

        Returns:
            Public URL if successful, None otherwise
        """
        if not self.is_enabled:
            logger.info("Ngrok is disabled in configuration")
            return None

        try:
            from pyngrok import ngrok, conf

            # Configure ngrok
            ngrok_config = self.config.ngrok

            if ngrok_config.auth_token:
                ngrok.set_auth_token(ngrok_config.auth_token)

            # Set region
            pyngrok_config = conf.get_default()
            pyngrok_config.region = ngrok_config.region

            # Start tunnel
            if ngrok_config.domain:
                # Use custom domain (requires paid plan)
                self._tunnel = ngrok.connect(
                    port,
                    hostname=ngrok_config.domain,
                )
            else:
                self._tunnel = ngrok.connect(port)

            self._public_url = self._tunnel.public_url
            logger.info(f"Ngrok tunnel started: {self._public_url}")

            return self._public_url

        except ImportError:
            logger.error("pyngrok not installed. Install with: pip install pyngrok")
            return None
        except Exception as e:
            logger.error(f"Failed to start ngrok tunnel: {e}")
            return None

    def stop(self) -> None:
        """Stop the ngrok tunnel."""
        if self._tunnel:
            try:
                from pyngrok import ngrok

                ngrok.disconnect(self._tunnel.public_url)
                logger.info("Ngrok tunnel stopped")
            except Exception as e:
                logger.error(f"Error stopping ngrok tunnel: {e}")
            finally:
                self._tunnel = None
                self._public_url = None


# Singleton instance
_ngrok_tunnel: Optional[NgrokTunnel] = None


def get_ngrok_tunnel() -> NgrokTunnel:
    """Get ngrok tunnel singleton instance."""
    global _ngrok_tunnel
    if _ngrok_tunnel is None:
        _ngrok_tunnel = NgrokTunnel()
    return _ngrok_tunnel
