from setuptools import setup, find_packages
setup(
    name = "SQLAlchemyAggregator",
    version = "0.1",
    packages = find_packages(),
    test_suite = "tests/simpletest",

    install_requires = ['SQLAlchemy>=0.4dev'],

    author = "Paul Colomiets",
    author_email = "pc@gafol.net",
    description = "SQLAlchemy's mapper extension which can"
        "automatically track changes in mapped classes and"
        "calculate aggregations based on them",
    license = "MIT",
    keywords = "sql sqlalchemy aggragation database",
    url = "http://www.mr-pc.kiev.ua/en/projects/SQLAlchemyAggregator",
)
