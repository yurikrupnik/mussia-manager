default:
    echo 'Hello, world!'
    uv python list
    node -v
cluster:
  gcloud beta container --project "playground-447016" clusters create-auto "vertex-cluster" --region "me-west1" --release-channel "regular" --tier "standard" --enable-ip-access --no-enable-google-cloud-access --network "projects/playground-447016/global/networks/default" --subnetwork "projects/playground-447016/regions/me-west1/subnetworks/default" --cluster-ipv4-cidr "/17" --binauthz-evaluation-mode=DISABLED --fleet-project=playground-447016 --enable-ray-operator --enable-ray-cluster-logging --enable-ray-cluster-monitoring --enable-dataplane-v2-flow-observability
  gcloud container clusters get-credentials vertex-cluster --region me-west1 --project playground-447016
  gcloud beta container --project "playground-447016" clusters create "cluster-1" --zone "europe-central2-a" --tier "standard" --no-enable-basic-auth --cluster-version "1.31.6-gke.1020000" --release-channel "regular" --machine-type "e2-standard-2" --image-type "COS_CONTAINERD" --disk-type "pd-balanced" --disk-size "100" --node-labels app=real --metadata disable-legacy-endpoints=true --node-taints app=real:NoSchedule --service-account "secret-puller@playground-447016.iam.gserviceaccount.com" --spot --num-nodes "3" --logging=SYSTEM,WORKLOAD --monitoring=SYSTEM,STORAGE,POD,DEPLOYMENT,STATEFULSET,DAEMONSET,HPA,CADVISOR,KUBELET --enable-private-nodes --enable-ip-alias --network "projects/playground-447016/global/networks/primary-network" --subnetwork "projects/playground-447016/regions/europe-central2/subnetworks/private-subnet" --enable-intra-node-visibility --default-max-pods-per-node "110" --enable-autoscaling --min-nodes "0" --max-nodes "3" --location-policy "ANY" --enable-ip-access --security-posture=standard --workload-vulnerability-scanning=standard --enable-dataplane-v2 --enable-dataplane-v2-metrics --enable-dataplane-v2-flow-observability --enable-multi-networking --no-enable-google-cloud-access --addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver,ConfigConnector,GcpFilestoreCsiDriver,GcsFuseCsiDriver --enable-ray-operator --enable-ray-cluster-logging --enable-ray-cluster-monitoring --enable-autoupgrade --enable-autorepair --max-surge-upgrade 1 --max-unavailable-upgrade 0 --binauthz-evaluation-mode=DISABLED --enable-autoprovisioning --min-cpu 1 --max-cpu 1 --min-memory 1 --max-memory 1 --enable-autoprovisioning-autorepair --enable-autoprovisioning-autoupgrade --autoprovisioning-max-surge-upgrade 1 --autoprovisioning-max-unavailable-upgrade 0 --enable-managed-prometheus --enable-vertical-pod-autoscaling --workload-pool "playground-447016.svc.id.goog" --enable-shielded-nodes --shielded-integrity-monitoring --no-shielded-secure-boot --enable-l4-ilb-subsetting --enable-image-streaming --fleet-project=playground-447016 --node-locations "europe-central2-a" && gcloud beta container --project "playground-447016" node-pools create "batch" --cluster "cluster-1" --zone "europe-central2-a" --machine-type "e2-medium" --image-type "COS_CONTAINERD" --disk-type "pd-balanced" --disk-size "100" --node-labels app=batch --labels app=batch --metadata disable-legacy-endpoints=true --node-taints app=batch:NoSchedule --service-account "iac-manager@playground-447016.iam.gserviceaccount.com" --spot --num-nodes "3" --enable-autoscaling --min-nodes "0" --max-nodes "3" --location-policy "ANY" --enable-autoupgrade --enable-autorepair --max-surge-upgrade 1 --max-unavailable-upgrade 0 --shielded-integrity-monitoring --no-shielded-secure-boot --node-locations "europe-central2-a"
#  works
#  does not work
lint:
  pnpm nx run-many -t lint --parallel --max-parallel=10 --prod
  uvx ruff check ./apps/python/ ./libs/python/
  uvx ruff format ./apps/python/ ./libs/python/
#  mpmrc, pypirc and docker configuration inits
sync:
  gcloud artifacts print-settings npm \
        --project=playground-447016 \
        --repository=npm-shared \
        --location=me-west1 \
        --scope=@superman >> .npmrc
  gcloud artifacts print-settings python \
      --project=playground-447016 \
      --repository=py-shared \
      --location=me-west1 >> .pypirc
  gcloud auth configure-docker me-west1-docker.pkg.dev
  uv sync # fails

build:
  pnpm nx run-many -t build --parallel --max-parallel=10 --prod
  uv build ./apps/python/agent2
test:
  pnpm nx run-many -t test --parallel --max-parallel=10 --prod
#  uv build ./apps/python/agent2
graph:
  uv tree
  pnpm nx graph

test-specific:
  pnpm nx run cli_tui1 -t test --parallel --max-parallel=10 --prod
  uv build ./apps/python/agent2/
setup-gcp-project:
  gcloud auth configure-docker \
      me-west1-docker.pkg.dev
  gcloud artifacts print-settings npm \
        --project=playground-447016 \
        --repository=npm-shared \
        --location=me-west1 \
        --scope=@superman >> .npmrc
  gcloud artifacts print-settings python \
      --project=playground-447016 \
      --repository=py-shared \
      --location=me-west1 >> .pypirc
  npx google-artifactregistry-auth .
dsa:
  nx-run test
init:
  -kind create cluster --config ./manifests/cluster/cluster.yaml
  istioctl install --set profile=demo -y

run-command command ass:
    pnpm nx {{ass}} -t {{command}} --parallel --max-parallel=10
#    cpi=$(sysctl -n hw.ncpu)
#    echo $cpi
