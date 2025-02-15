build:
	docker build -t frzquantum/hit-star-gateway:1.0 . 
run: build
	docker run -itd --name hit-star-gateway --net=host -p 7890:7890 -p 9090:9090 frzquantum/hit-star-gateway:1.0
stop:
	docker stop hit-star-gateway
remove: stop
	docker rm hit-star-gateway
exec:
	docker exec -it hit-star-gateway bash
