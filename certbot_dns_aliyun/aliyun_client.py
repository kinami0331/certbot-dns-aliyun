import logging

from certbot.errors import PluginError
from alibabacloud_alidns20150109.client import Client
from alibabacloud_alidns20150109.models import (
    DescribeDomainsRequest,
    AddDomainRecordRequest,
    DescribeDomainRecordsRequest,
    DeleteDomainRecordRequest,
)
from alibabacloud_tea_openapi.models import Config
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)


class AliyunClient:
    """
    Encapsulates all communication with the Aliyun DNS Serivce.
    """

    def __init__(self, access_key_id: str, access_key_secret: str, region_id: str, ttl: int) -> None:
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.region_id = region_id
        self.ttl = ttl
        self.client = Client(
            Config(
                access_key_id=access_key_id,
                access_key_secret=access_key_secret,
                region_id=region_id,
            )
        )

    def _find_domain_name(self, domain: str) -> str:
        domain_name_guesses = dns_common.base_domain_name_guesses(domain)
        for domain_name in domain_name_guesses:
            request = DescribeDomainsRequest(key_word=domain_name)
            response = self.client.describe_domains(request)
            if response.body and response.body.domains:
                for domain_info in response.body.domains.domain:
                    if domain_info.domain_name == domain_name:
                        return domain_name
        raise PluginError(f'Unable to determine domain name for {domain} using guesses: {domain_name_guesses}.')

    def _find_domain_record_id(self, domain: str, rr_keyword: str, record_type: str, value: str) -> str:
        request = DescribeDomainRecordsRequest(
            domain_name=domain,
            rrkey_word=rr_keyword,
            type=record_type,
            value_key_word=value,
        )
        response = self.client.describe_domain_records(request)
        if response.body and response.body.domain_records:
            for record in response.body.domain_records.record:
                if record.rr == rr_keyword:
                    return str(record.record_id)
        raise PluginError(
            f'Unable to find domain record for {domain} with rr keyword {rr_keyword}, record type {record_type}, and value {value}.'
        )

    def add_txt_record(self, domain: str, record_name: str, value: str) -> None:
        domain_name = self._find_domain_name(domain)
        rr = record_name[: record_name.rindex('.' + domain_name)]
        request = AddDomainRecordRequest(
            domain_name=domain_name,
            rr=rr,
            type='TXT',
            value=value,
            ttl=self.ttl,
        )
        response = self.client.add_domain_record(request)
        if response.body and response.body.record_id:
            logger.info(
                f'Successfully added TXT record for {domain} with record name {record_name} and value {value}. Record ID: {response.body.record_id}.'
            )
        else:
            raise PluginError(
                f'Failed to add TXT record for {domain} with record name {record_name} and value {value}.'
            )

    def del_txt_record(self, domain: str, record_name: str, value: str) -> None:
        domain_name = self._find_domain_name(domain)
        rr = record_name[: record_name.rindex('.' + domain_name)]
        record_id = self._find_domain_record_id(domain_name, rr, 'TXT', value)
        request = DeleteDomainRecordRequest(record_id=record_id)
        self.client.delete_domain_record(request)
