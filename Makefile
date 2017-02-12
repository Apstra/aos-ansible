
build:
	docker build -t apstra/aos-ansible .

run:
	docker run -t -i apstra/aos-ansible sh

test:
	docker run -t -i -v $(shell pwd):/project apstra/aos-ansible ansible-playbook -i tests/ravello.ini tests/pb.rav.test.yaml --syntax-check
