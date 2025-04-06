pipeline {
    agent any

    environment {
        GIT_CREDENTIALS_ID = 'github-credentials'
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
            // 💅 Clean up old model folder if it exists
            if (fileExists("${MODEL_DIR}")) {
                echo "🧹 Cleaning existing model directory..."
                bat "rmdir /s /q \"${MODEL_DIR}\""
            }

            // 📥 Clone GPT-2
            echo "📥 Cloning model from GitHub: ${params.MODEL_GIT_URL}"
            bat "git clone ${params.MODEL_GIT_URL} \"${MODEL_DIR}\""

            // 🫶 Copy dataset.json and model_info.json from this repo to Model/
            echo "🧾 Copying dataset and model info files into model directory..."
            bat "copy \"${env.WORKSPACE}\\dataset.json\" \"${MODEL_DIR}\\dataset.json\""
            bat "copy \"${env.WORKSPACE}\\model_info.json\" \"${MODEL_DIR}\\model_info.json\""

            // ✅ Validate
            def datasetExists = fileExists("${MODEL_DIR}\\dataset.json")
            def modelInfoExists = fileExists("${MODEL_DIR}\\model_info.json")
            if (!datasetExists || !modelInfoExists) {
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
                    bat "mkdir \"${TOOLS_DIR}\""

powershell '''
$workspace = "$env:WORKSPACE"
$toolsDir = Join-Path -Path $workspace -ChildPath "tools"
$syftExePath = Join-Path -Path $toolsDir -ChildPath "syft.exe"
$trivyZipPath = Join-Path -Path $toolsDir -ChildPath "trivy.zip"
$trivyExtractedDir = Join-Path -Path $toolsDir -ChildPath "trivy"
$trivyExePath = Join-Path -Path $trivyExtractedDir -ChildPath "trivy.exe"

New-Item -ItemType Directory -Force -Path $toolsDir

# ✅ SYFT download
$syftUrl = "https://github.com/anchore/syft/releases/download/v1.2.0/syft_1.2.0_windows_amd64.exe"
curl.exe -L -o "$syftExePath" "$syftUrl"

# ✅ TRIVY download
$trivyUrl = "https://github.com/aquasecurity/trivy/releases/download/v0.51.1/trivy_0.51.1_Windows-64bit.zip"
curl.exe -L -o "$trivyZipPath" "$trivyUrl"
Expand-Archive -Path $trivyZipPath -DestinationPath $trivyExtractedDir -Force

$env:PATH += ";$toolsDir;$trivyExtractedDir"
Write-Host "✅ Syft and Trivy installed successfully!"
'''

                    echo "🚀 Running AIBOM generator..."
                    bat "\"C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python313\\python.exe\" \"${MODEL_DIR}\\generate_aibom.py\" --model-path \"${MODEL_DIR}\""

                    echo "📁 Creating reports directory..."
                    bat "mkdir \"${REPORT_DIR}\""

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

                    echo "✅ Promote stage completed successfully."

                    echo "📢 CI/CD Pipeline completed successfully!"
                    echo "Generated Reports:"
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
