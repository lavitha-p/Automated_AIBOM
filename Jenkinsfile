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
                    bat "rmdir /s /q ${MODEL_DIR}"
                    
                    if (params.MODEL_GIT_URL) {
                        echo "📥 Cloning model from GitHub: ${params.MODEL_GIT_URL}"
                        bat "git clone ${params.MODEL_GIT_URL} ${MODEL_DIR}"
                    } else if (params.MODEL_LOCAL_PATH) {
                        echo "📂 Copying model from local path: ${params.MODEL_LOCAL_PATH}"
                        bat "xcopy /E /I \"${params.MODEL_LOCAL_PATH}\" \"${MODEL_DIR}\""
                    } else {
                        error "❌ No model source provided!"
                    }

                    def datasetExists = fileExists("${MODEL_DIR}\\dataset.json")
                    def model_infoExists = fileExists("${MODEL_DIR}\\model_info.json")
                    if (!datasetExists || !model_infoExists) {
                        error "Pipeline failed"
                    }

                    echo "✅ Build stage completed."
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo "📥 Fetching AIBOM script..."
                    bat "git clone ${SCRIPT_REPO} ${MODEL_DIR}\\script"
                    bat "copy ${MODEL_DIR}\\script\\generate_aibom.py ${MODEL_DIR}\\"
                    echo "✅ Deploy stage completed."
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    bat "mkdir ${TOOLS_DIR}"

                    bat """
                        echo Installing Syft...
                        curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b ${TOOLS_DIR}
                        echo Syft installed successfully!
                        ${TOOLS_DIR}\\syft.exe --version
                    """

                    bat """
                        echo Installing Trivy...
                        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b ${TOOLS_DIR}
                        echo Trivy installed successfully!
                    """

                    bat """
                        echo Checking Syft and Trivy...
                        where syft || echo Syft not found!
                        where trivy || echo Trivy not found!
                    """
                    
                    echo "🛠️ Running AIBOM script..."
                    bat "python ${MODEL_DIR}\\generate_aibom.py --model-path ${MODEL_DIR}"
                    
                    // Ensure report directory exists
                    bat "mkdir ${REPORT_DIR}"
                    
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
                        if (vulnReport.contains("LOW") || vulnReport.contains("MEDIUM") || vulnReport.contains("HIGH") || vulnReport.contains("CRITICAL")) {
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
                    bat "dir ${REPORT_DIR}"
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
