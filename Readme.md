# Bulma to Tailwind CSS Converter

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

This project converts Laaravel blade templates from Bulma CSS to Tailwind CSS using calls to a large language model (LLM) API. It simplifies the process of modernizing Bulma CSS-based templates to Tailwind CSS while maintaining functionality and readability.

It can optionally add in A11Y html/css and attempt to add responsive tailwind/html into the template.


## Repository

- GitHub Repository: [ohnotnow/bulma2tailwind](https://github.com/ohnotnow/bulma2tailwind)

## Installation

To set up this project, follow these steps:

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/ohnotnow/bulma2tailwind.git
   cd bulma2tailwind
   ```

2. Set up a virtual environment and install dependencies from `requirements.txt`:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

## Running the Code

To run the code and convert Bulma CSS-based templates to Tailwind CSS, use the following steps:

1. Activate the virtual environment:

   ```bash
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate  # Windows
   ```

2. Execute the main script:

   ```bash
   export OPENAI_API_KEY=sk-.....
   cd /path/to/your/templates
   python /path/to/cloned/repo/main.py
   ```

This will start the conversion process, scanning for Laravel Blade templates with Bulma CSS and converting them to Tailwind CSS.

## Alternate options to run
```bash
export OPENAI_API_KEY=sk-....
python main.py --file=/path/to/single/template.blade.php
python main.py --dir=/path/to/template/base/dir/
# optionally add a11y and responsive features - can be combined with other flags or omitted
python main.py --a11y --responsive
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
