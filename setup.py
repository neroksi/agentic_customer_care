from setuptools import find_packages, setup  # type: ignore


def do_setup():
    install_requires = [
        "pandas",
        "openpyxl",
        "openai",
        "pydantic",
        "python-dotenv",
        "Jinja2",
    ]

    extras: dict[str, list[str]] = {}

    extras["notebook"] = [
        "notebook",
        "ipykernel",
        "ipywidgets",
    ]

    extras["all"] = sorted(
        set([rqrmt for _, flavour_rqrmts in extras.items() for rqrmt in flavour_rqrmts])
    )

    extras["dev"] = extras["all"]

    setup(
        name="agentic_customer_care",
        version="0.0.1",
        description="Agentic AI Customer Care",
        author="neroksi",
        author_email="nkossy.pro@gmail.com",
        url="https://github.com/neroksi/agentic_customer_care",
        license="Apache 2.0",
        packages=find_packages("src"),
        package_dir={"": "src"},
        # python_requires=">=3.11.11",
        install_requires=install_requires,
        extras_require=extras,
        classifiers=[
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
        ],
        keywords="Agentic AI Customer Care",
    )


if __name__ == "__main__":
    do_setup()
