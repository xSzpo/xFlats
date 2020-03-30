**Kubernetes swith between clusters**

[www: Switch Between Multiple Kubernetes Clusters With Ease](https://nikgrozev.com/2019/10/03/switch-between-multiple-kubernetes-clusters-with-ease/)

* list all preconfigured contexts and see which one is active `kubectl config get-contexts`
```
(base) Daniels-MacBook-Pro:201907_xFlats xszpo$ kubectl config get-contexts
CURRENT   NAME                                   CLUSTER                                AUTHINFO                               NAMESPACE
          docker-desktop                         docker-desktop                         docker-desktop
          docker-for-desktop                     docker-desktop                         docker-desktop
*         gke_xflats-271719_us-east1-b_xszpo01   gke_xflats-271719_us-east1-b_xszpo01   gke_xflats-271719_us-east1-b_xszpo01
```
* get the name of the active context/cluster `kubectl config get-contexts`
```
(base) Daniels-MacBook-Pro:201907_xFlats xszpo$ kubectl config get-contexts
CURRENT   NAME                                   CLUSTER                                AUTHINFO                               NAMESPACE
          docker-desktop                         docker-desktop                         docker-desktop
          docker-for-desktop                     docker-desktop                         docker-desktop
*         gke_xflats-271719_us-east1-b_xszpo01   gke_xflats-271719_us-east1-b_xszpo01   gke_xflats-271719_us-east1-b_xszpo01
```
* switch between the predefined contexts `kubectl config current-context`
```
(base) Daniels-MacBook-Pro:201907_xFlats xszpo$ kubectl config current-context
gke_xflats-271719_us-east1-b_xszpo01
```
* `kubectl config current-context`
```
kubectl config use-context NikTest
```