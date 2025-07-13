import logging
from typing import Callable, Optional
from certbot import errors
from certbot import configuration
from certbot.plugins import dns_common
from certbot.plugins.dns_common import CredentialsConfiguration
from .aliyun_client import AliyunClient

logger = logging.getLogger(__name__)


class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Aliyun

    This Authenticator uses the Aliyun API to fulfill a dns-01 challenge.
    """

    description = 'Obtain certificates using a DNS TXT record (if you are using Aliyun for DNS).'
    ttl = 600

    def __init__(self, config: configuration.NamespaceConfig, name: str):
        super().__init__(config, name)
        self.credentials: Optional[CredentialsConfiguration] = None

    @classmethod
    def add_parser_arguments(cls, add: Callable[..., None], default_propagation_seconds: int = 10) -> None:
        super().add_parser_arguments(add, default_propagation_seconds)
        add('credentials', help='Aliyun credentials INI file.')

    def more_info(self) -> str:
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using the Aliyun API.'

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            'credentials',
            'Aliyun credentials INI file',
            {
                'access_key_id': 'AccessKey Id for Aliyun',
                'access_key_secret': 'AccessKey Secret for Aliyun',
            },
        )

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        self._get_aliyun_client().add_txt_record(domain, validation_name, validation)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        self._get_aliyun_client().del_txt_record(domain, validation_name, validation)

    def _get_aliyun_client(self) -> AliyunClient:
        if not self.credentials:
            raise errors.Error('Aliyun credentials not configured')

        access_key_id = self.credentials.conf('access_key_id')
        access_key_secret = self.credentials.conf('access_key_secret')
        region_id = self.credentials.conf('region-id') or 'cn-hangzhou'

        if not access_key_id or not access_key_secret:
            raise errors.Error('Aliyun credentials not configured')

        return AliyunClient(access_key_id, access_key_secret, region_id, self.ttl)
