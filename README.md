<div id="top"></div>

<div align="center" class="text-center">
<h1>MANUTENCAO - Sistema Inteligente de Gerenciamento de Manutenção</h1>
<p><em>Empowering Maintenance Excellence Through Intelligent Management</em></p>

<img alt="last-commit" src="https://img.shields.io/github/last-commit/theofeitoza/manutencao?style=flat&logo=git&logoColor=white&color=0080ff" class="inline-block mx-1">
<img alt="repo-top-language" src="https://img.shields.io/github/languages/top/theofeitoza/manutencao?style=flat&color=0080ff" class="inline-block mx-1">
<img alt="repo-language-count" src="https://img.shields.io/github/languages/count/theofeitoza/manutencao?style=flat&color=0080ff" class="inline-block mx-1">
<p><em>Built with the tools and technologies:</em></p>
<img alt="Python" src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" class="inline-block mx-1">
<img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=flat&logo=Streamlit&logoColor=white">
<img alt="SQLite" src="https://img.shields.io/badge/SQLite-003B57.svg?style=flat&logo=SQLite&logoColor=white">
</div>
<br>
<hr>
<h2>Table of Contents</h2>
<ul class="list-disc pl-4 my-0">
<li class="my-0"><a href="#overview">Overview</a></li>
<li class="my-0"><a href="#features">Features</a></li>
<li class="my-0"><a href="#getting-started">Getting Started</a>
<ul class="list-disc pl-4 my-0">
<li class="my-0"><a href="#prerequisites">Prerequisites</a></li>
<li class="my-0"><a href="#installation">Installation</a></li>
<li class="my-0"><a href="#usage">Usage</a></li>
<li class="my-0"><a href="#testing">Testing</a></li>
</ul>
</li>
<li class="my-0"><a href="#screenshots">Screenshots</a></li>
</ul>
<hr>
<h2 id="overview">Overview</h2>
<p>manutencao is an all-in-one maintenance management system that provides a rich, interactive interface for overseeing maintenance workflows, equipment, personnel, and parts. It integrates core functionalities such as data management, analytics dashboards, log monitoring, and report generation to support efficient and transparent operations.</p>
<p><strong>Why manutencao?</strong></p>
<p>This project helps developers build and maintain robust maintenance workflows with ease. The core features include:</p>
<ul class="list-disc pl-4 my-0">
<li class="my-0">🛠️ <strong>Dashboard &amp; Visualizations:</strong> Aggregates key metrics and project timelines for real-time operational insights.</li>
<li class="my-0">🔒 <strong>Secure Data &amp; Authentication:</strong> Ensures data integrity and user access control across the system.</li>
<li class="my-0">📊 <strong>Logs &amp; Auditability:</strong> Provides detailed change histories for transparency and compliance.</li>
<li class="my-0">🧩 <strong>Modular Data Management:</strong> Facilitates seamless CRUD operations for equipment, personnel, parts, and orders.</li>
<li class="my-0">📄 <strong>Reporting &amp; Export:</strong> Generates detailed PDFs for documentation and analysis.</li>
<li class="my-0">⚙️ <strong>Interactive UI Components:</strong> Dynamic tables and dialogs streamline user interactions and data editing.</li>
</ul>
<hr>
<h2 id="features">Features</h2>
<p>The platform offers a robust set of modules for comprehensive management:</p>
<ul>
    <li>🔐 <strong>Login e Autenticação:</strong> Sistema de login seguro para controle de acesso.</li>
    <li>📊 <strong>Dashboard de Gerenciamento:</strong> Visão geral de KPIs e status de manutenção.</li>
    <li>📝 <strong>Gestão de Ordens de Serviço:</strong> Criação, atribuição, monitoramento e conclusão de ordens.</li>
    <li>👨‍🏭 <strong>Cadastro de Funcionários:</strong> Gerenciamento de dados de técnicos e equipes.</li>
    <li>⚙️ <strong>Cadastro de Peças e Equipamentos:</strong> Registro detalhado de ativos e seus componentes.</li>
    <li>📈 <strong>Visualização de Gantt:</strong> Planejamento e acompanhamento de tarefas em um gráfico de Gantt.</li>
    <li>📄 <strong>Geração de Relatórios PDF:</strong> Exportação de dados e ordens de serviço.</li>
    <li>🔍 <strong>Visualizador de Logs:</strong> Auditoria completa das ações do sistema.</li>
</ul>

<hr>
<h2 id="getting-started">Getting Started</h2>
<h3>Prerequisites</h3>
<p>This project requires the following dependencies:</p>
<ul class="list-disc pl-4 my-0">
<li class="my-0"><strong>Programming Language:</strong> Python 3.8+</li>
<li class="my-0"><strong>Package Manager:</strong> pip</li>
</ul>
<h3>Installation</h3>
<p>Build manutencao from the source and install dependencies:</p>
<ol>
<li class="my-0">
<p><strong>Clone the repository:</strong></p>
<pre><code class="language-sh">❯ git clone https://github.com/theofeitoza/manutencao
</code></pre>
</li>
<li class="my-0">
<p><strong>Navigate to the project directory:</strong></p>
<pre><code class="language-sh">❯ cd manutencao
</code></pre>
</li>
<li class="my-0">
<p><strong>Create a virtual environment (recommended):</strong></p>
<pre><code class="language-sh"># For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
</code></pre>
</li>
<li class="my-0">
<p><strong>Install the dependencies:</strong></p>
<pre><code class="language-sh">❯ pip install -r requirements.txt
</code></pre>
*(Note: If `requirements.txt` is not available, you might need to install Streamlit, Pandas, SQLite-related libraries manually).*
</li>
</ol>
<h3>Usage</h3>
<p>Run the project with:</p>
<pre><code class="language-sh">streamlit run main.py
</code></pre>
<p>Then, open your web browser and navigate to the address provided in the terminal (usually <code>http://localhost:8501</code>).</p>

<h3>Testing</h3>
<p>Manutencao uses the {<strong>test_framework</strong>} test framework. Run the test suite with:</p>
<p><strong>Using <a href="https://docs.conda.io/">conda</a>:</strong></p>
<pre><code class="language-sh">conda activate {venv}
pytest
</code></pre>

<hr>
<h2 id="screenshots">Screenshots</h2>

### Tela de Login
<p align="center">
  <img src="login.png" alt="Tela de Login" width="60%">
</p>

### Dashboard Principal
<p align="center">
  <img src="Dashboard.png" alt="Dashboard Principal" width="80%">
</p>

### Gestão de Ordens de Serviço
<p align="center">
  <img src="Ordens de Servico.png" alt="Gestão de Ordens de Serviço" width="80%">
</p>

### Cadastro de Funcionários
<p align="center">
  <img src="Funcionarios.png" alt="Cadastro de Funcionários" width="80%">
</p>

### Cadastro de Peças
<p align="center">
  <img src="Pecas.png" alt="Cadastro de Peças" width="80%">
</p>

### Diagrama de Gantt
<p align="center">
  <img src="Diagrama de Gantt.png" alt="Diagrama de Gantt" width="80%">
</p>

### Aplicação do Técnico
<p align="center">
  <img src="Aplicação do Tecnico.jpg" alt="Aplicação do Técnico" width="80%">
</p>

### Banco de Dados
<p align="center">
  <img src="Banco de Dados.png" alt="Estrutura do Banco de Dados" width="80%">
</p>

<hr>
<div align="left" class=""><a href="#top">⬆ Return</a></div>
<hr>
