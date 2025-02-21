VERSION = 1.3
build:
	docker build -t frzquantum/hit-star-gateway:$(VERSION) . 
run: build
	docker run -itd --name hit-star-gateway frzquantum/hit-star-gateway:$(VERSION)
stop:
	docker stop hit-star-gateway
remove: stop
	docker rm hit-star-gateway
exec:
	docker exec -it hit-star-gateway bash
supervisorctl:
	docker exec -it hit-star-gateway supervisorctl status
push:
	docker push frzquantum/hit-star-gateway:$(VERSION)
