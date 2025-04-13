pipeline {
    agent any

    environment {
        GIT_CREDENTIALS_ID = 'github-credentials'
        PYTHON_PATH = 'C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python313\\python.exe' // 🔥 YOU MISSED THIS
        MODEL_DIR = "${WORKSPACE}\\Model"
        SCRIPT_REPO = 'https://github.com/lavitha-p/Automated_AIBOM.git'
        REPORT_DIR = "${MODEL_DIR}\\reports"
        TOOLS_DIR = "${MODEL_DIR}\\tools"
    }

    parameters {
        string(name: 'MODEL_GIT_URL', defaultValue: '', description: 'Enter GitHub repo URL for the model (leave empty if using local path)')
        string(name: 'MODEL_LOCAL_PATH', defaultValue: '', description: 'Enter local model path (leave empty if using GitHub)')
    }

    stages {
        stage('Build') {
            steps {
                script {
                    if (fileExists("${MODEL_DIR}")) {
                        echo "🧹 Cleaning existing model directory..."
                        bat "rmdir /s /q \"${MODEL_DIR}\""
                    }

                    echo "📥 Cloning model from GitHub: ${params.MODEL_GIT_URL}"
                    bat "git clone ${params.MODEL_GIT_URL} \"${MODEL_DIR}\""

                    echo "🧾 Copying dataset and model info files into model directory..."
                    bat "copy \"${env.WORKSPACE}\\dataset.json\" \"${MODEL_DIR}\\dataset.json\""
                    bat "copy \"${env.WORKSPACE}\\model_info.json\" \"${MODEL_DIR}\\model_info.json\""

                    if (!fileExists("${MODEL_DIR}\\dataset.json") || !fileExists("${MODEL_DIR}\\model_info.json")) {
                        error "❌ Required files dataset.json or model_info.json not found!"
                    }

                    echo "✅ Build stage completed."
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo "📥 Fetching AIBOM script..."
                    bat "git clone ${SCRIPT_REPO} \"${MODEL_DIR}\\script\""
                    bat "copy \"${MODEL_DIR}\\script\\generate_aibom.py\" \"${MODEL_DIR}\\\""
                    echo "✅ Deploy stage completed."
                }
            }
        }

stage('Test') {
    steps {
        script {
            echo "🧰 Installing Syft and Trivy..."

            bat "mkdir \"${TOOLS_DIR}\""

            powershell '''
            $toolsDir = "${env:TOOLS_DIR}"
            $syftExe = Join-Path $toolsDir "syft.exe"
            $trivyZip = Join-Path $toolsDir "trivy.zip"
            $trivyDir = Join-Path $toolsDir "trivy"
            $trivyExe = Join-Path $trivyDir "trivy.exe"

            curl.exe -L -o $syftExe "https://github.com/anchore/syft/releases/download/v1.2.0/syft_1.2.0_windows_amd64.exe"
            curl.exe -L -o $trivyZip "https://github.com/aquasecurity/trivy/releases/download/v0.51.1/trivy_0.51.1_Windows-64bit.zip"
            Expand-Archive -Path $trivyZip -DestinationPath $trivyDir -Force

            $env:PATH += ";$toolsDir;$trivyDir"
            Write-Host "✅ Syft and Trivy installed."
            '''

            echo "📦 Installing Python dependencies..."
            bat "\"${env.PYTHON_PATH}\" -m pip install --upgrade pip"
            bat "\"${env.PYTHON_PATH}\" -m pip install psutil pandas"

            echo "📁 Creating report folder: ${REPORT_DIR}"
            bat "mkdir \"${REPORT_DIR}\""

            echo "🚀 Running AIBOM generator..."
            bat "\"${env.PYTHON_PATH}\" \"${MODEL_DIR}\\generate_aibom.py\" --model-path \"${MODEL_DIR}\" --output-dir \"${REPORT_DIR}\""

            echo "✅ Test stage completed."
        }
    }
}

        stage('Promote') {
            steps {
                script {
                    def vulnReportPath = "${REPORT_DIR}\\vulnerability.json"
                    def aibomExists = fileExists("${REPORT_DIR}\\aibom.json")
                    def sbomExists = fileExists("${REPORT_DIR}\\sbom.json")
                    def vulnExists = fileExists(vulnReportPath)

                    if (vulnExists) {
                        def vulnReport = readFile(vulnReportPath)
                        if (vulnReport =~ /LOW|MEDIUM|HIGH|CRITICAL/) {
                            echo "⚠️ WARNING: Model has vulnerabilities! Not ready for production."
                        } else {
                            echo "✅ Model passes security checks."
                        }
                    } else {
                        echo "⚠️ vulnerability.json not found. Skipping vulnerability check."
                    }

                    echo "✅ Promote stage completed."
                    echo "📢 CI/CD Pipeline completed successfully!"
                    echo "🧾 Generated Reports:"
                    bat "dir \"${REPORT_DIR}\""
                }
            }
        }
    }

    post {
        failure {
            echo "❌ Pipeline failed. Check logs for details."
        }
        success {
            echo "✅ Pipeline executed successfully."
        }
    }
}
