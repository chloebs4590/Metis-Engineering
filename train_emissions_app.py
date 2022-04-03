{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "name": "train_emissions_app.py",
      "provenance": [],
      "collapsed_sections": [],
      "authorship_tag": "ABX9TyPkKIRMxXNXSgNeLjA83qrF",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/chloebs4590/Metis-Engineering/blob/main/train_emissions_app.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "!pip install streamlit"
      ],
      "metadata": {
        "id": "vYQZTb2_lFZ3"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "!pip install tornado --upgrade"
      ],
      "metadata": {
        "id": "Rs3hFnPdmJ1x",
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "outputId": "5447404e-758c-4ea6-c2c3-b5701a30352c"
      },
      "execution_count": 2,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Requirement already satisfied: tornado in /usr/local/lib/python3.7/dist-packages (6.1)\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "!pip install config"
      ],
      "metadata": {
        "id": "ZxsTK6oboI_c"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "execution_count": 5,
      "metadata": {
        "id": "8mtIpv4egDO6"
      },
      "outputs": [],
      "source": [
        "import streamlit as st\n",
        "import pandas as pd\n",
        "import pydeck as pdk\n",
        "import config"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "st.set_page_config(layout=\"wide\")"
      ],
      "metadata": {
        "id": "5PJ0vyu7oORs"
      },
      "execution_count": 6,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        ""
      ],
      "metadata": {
        "id": "V7tYzw4qo3lr"
      },
      "execution_count": null,
      "outputs": []
    }
  ]
}