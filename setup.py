import setuptools


setuptools.setup(
    name="deployiptest",
    version="0.0.1",
    author="Paul Pietkiewicz",
    author_email="paul.pietkiewicz@acm.org",
    description="Test of Kubernetes Deployment IPs (assuming exposed as LoadBalancer)",
    url="https://github.com/platten/deployiptest",
    packages=setuptools.find_packages(),
    setup_requires=['pbr'],
    pbr=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
