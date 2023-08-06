from django.http import HttpResponse

from flashpolicies import policies


def simple(request, domains):
    """
    A simple Flash cross-domain access policy.

    **Required arguments:**

    ``domains``
        A list of domains from which to allow access. Each value may
        be either a domain name (e.g., ``example.com``) or a wildcard
        (e.g., ``*.example.com``). Due to serious potential security
        issues, it is strongly recommended that you not use wildcard
        domain values.

    **Optional arguments:**

    None.
    
    """
    return HttpResponse(policies.simple_policy(domains).toprettyxml(encoding='utf-8'),
                        content_type='text/x-cross-domain-policy')

def no_access(request):
    """
    A Flash cross-domain access policy which permits no access of any
    kind.
    
    **Required arguments:**

    None.

    **Optional arguments:**

    None.
    
    """
    return HttpResponse(policies.no_access_policy().toprettyxml(encoding='utf-8'),
                        content_type='text/x-cross-domain-policy')
