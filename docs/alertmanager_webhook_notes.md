# Alertmanager webhook notes

This configuration creates an Alertmanager routing tree that sends only selected alerts to a webhook receiver, while all unmatched alerts go to a fallback receiver named `null`.[cite:17][cite:35]

## Configuration

```yaml
alertmanager:
  config:
    global:
      resolve_timeout: 5m
    route:
      receiver: "null"
      group_by: [ "alertname", "cluster", "namespace" ]
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 12h
      routes:
        - receiver: "webhook"
          match:
            alertname: MinIODown
    receivers:
      - name: "null"
      - name: "webhook"
        webhook_configs:
          - url: "https://webhook.site/01fefc36-5543-4b45-b24e-1ec79b5e8f1d"
            send_resolved: true
```

## What each part means

### `global.resolve_timeout`

`resolve_timeout: 5m` tells Alertmanager how long to wait before considering an alert resolved when it stops receiving updates for that alert.[cite:17]

In practice, this helps avoid very fast flip-flopping between firing and resolved states during short interruptions.[cite:17]

### Root `route`

The top-level `route` is the default routing rule for all incoming alerts.[cite:17]

```yaml
route:
  receiver: "null"
  group_by: [ "alertname", "cluster", "namespace" ]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
```

Its fields mean:

- `receiver: "null"` sets the fallback destination for alerts that do not match any child route.[cite:17][cite:35]
- `group_by` tells Alertmanager to bundle alerts together when they share the same `alertname`, `cluster`, and `namespace` labels.[cite:17]
- `group_wait: 30s` waits up to 30 seconds before sending the first notification for a new alert group so related alerts can be batched together.[cite:17]
- `group_interval: 5m` waits 5 minutes before sending another notification for the same group after the first one, if new alerts join that group.[cite:17]
- `repeat_interval: 12h` resends a notification every 12 hours for an alert that is still firing.[cite:17]

### Child `routes`

The nested `routes` block defines more specific routing rules under the root route.[cite:17]

```yaml
routes:
  - receiver: "webhook"
    match:
      alertname: MinIODown
```

This means any alert whose `alertname` label is exactly `MinIODown` is sent to the `webhook` receiver instead of the root `null` receiver.[cite:17][cite:40]

The match is exact and case-sensitive, so `MinIODown`, `MinioDown`, and `miniodown` are treated as different values.[cite:40]

### `receivers`

A receiver defines where Alertmanager should send a notification after routing is decided.[cite:17]

```yaml
receivers:
  - name: "null"
  - name: "webhook"
    webhook_configs:
      - url: "https://webhook.site/..."
        send_resolved: true
```

- `null` is a valid named receiver used as a sink for alerts you do not want delivered anywhere.[cite:35]
- `webhook` sends an HTTP POST request to the configured URL.[cite:17]
- `send_resolved: true` tells Alertmanager to send another webhook when the alert changes from firing to resolved.[cite:17]

## How routing works

Alertmanager evaluates alerts against the routing tree and sends each alert to the first matching child route unless the configuration explicitly tells it to continue further.[cite:17]

For this configuration, the flow is:

1. An alert arrives from Prometheus.[cite:17]
2. Alertmanager starts at the root route.[cite:17]
3. It checks child routes for a match on `alertname: MinIODown`.[cite:17][cite:40]
4. If the alert matches, it goes to the `webhook` receiver.[cite:17]
5. If it does not match, it falls back to `receiver: "null"` on the root route.[cite:17][cite:35]

## Why the UI showed `null` earlier

When the alert name in the route did not exactly match the alert name produced by the Prometheus rule, Alertmanager could not match the child route, so it used the root receiver `null`.[cite:17][cite:40]

After the alert name and route matcher were made identical, the alert matched the child route and was delivered to webhook.site.[cite:17][cite:40]

## What webhook.site receives

When the route matches, Alertmanager sends a JSON payload to the webhook URL containing metadata about the alert group, labels, annotations, status, and timing information.[cite:17]

Because `send_resolved: true` is enabled, webhook.site receives both firing and resolved notifications for `MinIODown` alerts.[cite:17]
