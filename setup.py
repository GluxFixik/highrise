from setuptools import setup, find_packages

setup(
    name="highrise-bot-24-7",
    version="1.0.0",
    description="Highrise Bot 24/7 with moderation and VIP features",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "highrise-bot-sdk==19.1.0",
    ],
    python_requires=">=3.8",
) 