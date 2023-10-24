pipeline {
    options {
        buildDiscarder(logRotator(daysToKeepStr: '30'))
    }
    stages {
        stage('General settings') {
            steps {
                func call 1
            }
        }   

        // GIT repo update for a particular BRANCH passed as parameter
        stage('SCM GIT repo pull') {
            steps {
                func call 2
            }

        }

        // creates/updates all Jira Tests
        stage('Updating JIRA Tests') {

        }

        // conditional stage - checks device FW (passed as parameter) and updates if needed
        stage('device FW check and update') {
            // fetch device fw from backend
            // if FW not matched with passed FW param.
                // create DP using delta from DEVICE Jenkins Server
                // update device to particular new FW
        }

        stage ('test execution') {
            
        }
    }
}