# DeepHunter

[![CodeQL](https://github.com/Cyber-Threat-Hunting-Playground/deephunter/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/Cyber-Threat-Hunting-Playground/deephunter/actions/workflows/github-code-scanning/codeql)

DeepHunter is a Threat Hunting platform that features:

- Repository for your threat hunting analytics shown in a sortable table.
- Search and filters (description, threat hunting notes, tags, query, OS coverage, vulnerabilities, threat actors, threat names, MITRE coverage, etc.) to find particular threat hunting analytics or group them into hunting packages.
- Automated execution of threat hunting queries in daily campaigns and collection of daily statistics (number of matching events, number of matching endpoints, etc).
- Trend analysis with automatic detection of statistical anomalies.
- Timeline view of the distribution of threat hunting analytics for a given endpoint.
- Network view module to analyze network activities from a host, with highlights on the destination popularity (based on your environment) and VirusTotal reputation.
- Reports (Campaigns performance report, Top endpoints identified in the last campaign, MITRE coverage, List of analytics with missing MITRE coverage)
- Tools (LOL Driver Hash Checker, VirusTotal Hash Checker, Whois).

For more information, read the [documentation](https://deephunter.readthedocs.io/en/latest/).
