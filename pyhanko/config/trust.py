from datetime import timedelta

from pyhanko.config import api
from pyhanko.config.errors import ConfigurationError
from pyhanko.keys import load_certs_from_pemder

__all__ = ['init_validation_context_kwargs', 'parse_trust_config']


def init_validation_context_kwargs(
    *,
    trust,
    trust_replace,
    other_certs,
    retroactive_revinfo=False,
    time_tolerance=None,
):
    if not isinstance(time_tolerance, timedelta):
        if time_tolerance is None:
            time_tolerance = timedelta(seconds=DEFAULT_TIME_TOLERANCE)
        elif isinstance(time_tolerance, int):
            time_tolerance = timedelta(seconds=time_tolerance)
        else:
            raise ConfigurationError(
                "time-tolerance parameter must be specified in seconds"
            )
    vc_kwargs = {'time_tolerance': time_tolerance}
    if retroactive_revinfo:
        vc_kwargs['retroactive_revinfo'] = True
    if trust:
        if isinstance(trust, str):
            trust = (trust,)
        # add trust roots to the validation context, or replace them
        trust_certs = list(load_certs_from_pemder(trust))
        if trust_replace:
            vc_kwargs['trust_roots'] = trust_certs
        else:
            vc_kwargs['extra_trust_roots'] = trust_certs
    if other_certs:
        if isinstance(other_certs, str):
            other_certs = (other_certs,)
        vc_kwargs['other_certs'] = list(load_certs_from_pemder(other_certs))
    return vc_kwargs


def parse_trust_config(
    trust_config, time_tolerance, retroactive_revinfo
) -> dict:
    api.check_config_keys(
        'ValidationContext',
        (
            'trust',
            'trust-replace',
            'other-certs',
            'time-tolerance',
            'retroactive-revinfo',
            'signer-key-usage',
            'signer-extd-key-usage',
            'signer-key-usage-policy',
        ),
        trust_config,
    )
    return init_validation_context_kwargs(
        trust=trust_config.get('trust'),
        trust_replace=trust_config.get('trust-replace', False),
        other_certs=trust_config.get('other-certs'),
        time_tolerance=trust_config.get('time-tolerance', time_tolerance),
        retroactive_revinfo=trust_config.get(
            'retroactive-revinfo', retroactive_revinfo
        ),
    )


DEFAULT_TIME_TOLERANCE = 10
