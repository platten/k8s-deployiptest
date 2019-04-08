# k8s-deployiptest

[![Build Status](https://travis-ci.org/platten/k8s-deployiptest.svg?branch=master)](https://travis-ci.org/platten/k8s-deployiptest)

Test of Kubernetes Deployment IPs (assuming exposed as LoadBalancer)

```
docker run -ti -v ~/.kube:/root/.kube platten/k8s-deployiptest:latest
```