docker build -t tenniscale-image .
docker run --name tenniscale-container -d -p 8000:8000 -v $(pwd):/code tenniscale-image

#connect to turborepo
git subtree add --prefix=apps/tenniscale https://github.com/valiantlynx/tenniscale.git main --squash
git subtree pull --prefix=apps/tenniscale https://github.com/valiantlynx/tenniscale.git main --squash
git subtree push --prefix=apps/tenniscale https://github.com/valiantlynx/tenniscale.git main