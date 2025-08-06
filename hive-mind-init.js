#!/usr/bin/env node
/**
 * Film Crew AI - Hive Mind Initialization
 * Sets up the Claude Flow hive-mind configuration for the Film Crew AI system
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🎬 Film Crew AI - Hive Mind Setup Wizard\n');
console.log('============================================\n');

// Check if Claude Flow is installed
try {
    execSync('npx claude-flow@alpha --version', { stdio: 'ignore' });
    console.log('✓ Claude Flow detected\n');
} catch (error) {
    console.log('⚠ Claude Flow not detected. Installing...\n');
    try {
        execSync('npm install -g claude-flow@alpha', { stdio: 'inherit' });
    } catch (installError) {
        console.error('Failed to install Claude Flow. Please install manually:');
        console.error('npm install -g claude-flow@alpha');
        process.exit(1);
    }
}

// Read hive-mind configuration
const configPath = path.join(__dirname, '.claude-flow', 'hive-mind.json');
if (!fs.existsSync(configPath)) {
    console.error('❌ Hive mind configuration not found at:', configPath);
    process.exit(1);
}

const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

console.log(`📋 Loaded configuration: ${config.name}\n`);
console.log(`🤖 Agents configured: ${config.agents.length}`);
config.agents.forEach(agent => {
    console.log(`   - ${agent.name} (${agent.id})`);
});

console.log(`\n🔄 Workflows configured: ${config.workflows.length}`);
config.workflows.forEach(workflow => {
    console.log(`   - ${workflow.name} (${workflow.id})`);
});

console.log('\n============================================\n');

// Interactive setup
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function question(prompt) {
    return new Promise(resolve => {
        rl.question(prompt, resolve);
    });
}

async function runWizard() {
    console.log('🚀 Hive Mind Setup Options:\n');
    console.log('1. Initialize Python-based processing (Recommended)');
    console.log('2. Configure Claude Flow integration');
    console.log('3. Test agent orchestration');
    console.log('4. Process a script');
    console.log('5. Exit\n');
    
    const choice = await question('Select option (1-5): ');
    
    switch(choice.trim()) {
        case '1':
            console.log('\n✅ Python-based processing is already configured!');
            console.log('Run: python film_crew_ai.py --all');
            break;
            
        case '2':
            console.log('\n🔧 Configuring Claude Flow integration...');
            try {
                // Create Claude Flow specific config
                const claudeFlowConfig = {
                    ...config,
                    integration: {
                        type: 'claude-flow',
                        version: 'alpha',
                        swarmMode: true
                    }
                };
                
                fs.writeFileSync(
                    path.join(__dirname, '.claude-flow', 'swarm-config.json'),
                    JSON.stringify(claudeFlowConfig, null, 2)
                );
                
                console.log('✓ Claude Flow configuration created');
                console.log('Note: Claude Flow swarm mode requires additional setup');
            } catch (error) {
                console.error('Failed to configure:', error.message);
            }
            break;
            
        case '3':
            console.log('\n🧪 Testing agent orchestration...');
            console.log('Running: python film_crew_ai.py --script scripts/test_script.txt');
            try {
                execSync('python film_crew_ai.py --script scripts/test_script.txt', { 
                    stdio: 'inherit',
                    cwd: __dirname
                });
                console.log('\n✓ Agent orchestration test complete!');
            } catch (error) {
                console.error('Test failed:', error.message);
            }
            break;
            
        case '4':
            const scriptName = await question('\nEnter script filename (from scripts/ folder): ');
            if (scriptName) {
                console.log(`\nProcessing ${scriptName}...`);
                try {
                    execSync(`python film_crew_ai.py --script scripts/${scriptName}`, {
                        stdio: 'inherit',
                        cwd: __dirname
                    });
                    console.log('\n✓ Script processing complete!');
                } catch (error) {
                    console.error('Processing failed:', error.message);
                }
            }
            break;
            
        case '5':
            console.log('\nExiting wizard...');
            rl.close();
            return;
            
        default:
            console.log('\nInvalid option');
    }
    
    console.log('\n');
    await runWizard(); // Loop back to menu
}

// Run the wizard
runWizard().catch(error => {
    console.error('Wizard error:', error);
    rl.close();
});