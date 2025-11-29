document.addEventListener('DOMContentLoaded', function() {
    // Check if fitnessData is available (it's passed from the template)
    if (typeof fitnessData === 'undefined' || fitnessData.length === 0) {
        console.error('No fitness data available');
        return;
    }

    // Chart.js global defaults for better appearance
    Chart.defaults.font.family = "'Roboto', 'Helvetica', 'Arial', sans-serif";
    Chart.defaults.color = '#555';
    Chart.defaults.borderColor = '#eee';
    
    // Prepare data for charts
    const dates = fitnessData.map(entry => entry.date);
    const steps = fitnessData.map(entry => entry.steps);
    const calories = fitnessData.map(entry => entry.calories);
    const distance = fitnessData.map(entry => entry.distance);
    const veryActiveMinutes = fitnessData.map(entry => entry.veryActiveMinutes);
    const lightlyActiveMinutes = fitnessData.map(entry => entry.lightlyActiveMinutes);
    
    // Calculate cumulative steps and average steps per day
    const cumulativeSteps = calculateCumulative(steps);
    const totalSteps = cumulativeSteps[cumulativeSteps.length - 1] || 0;
    const avgSteps = totalSteps > 0 ? Math.round(totalSteps / steps.length) : 0;
    
    // Calculate total and average calories
    const totalCalories = calories.reduce((acc, curr) => acc + curr, 0);
    const avgCalories = totalCalories > 0 ? Math.round(totalCalories / calories.length) : 0;
    
    // Update summary metrics
    document.getElementById('totalStepsValue').textContent = totalSteps.toLocaleString();
    document.getElementById('avgStepsValue').textContent = avgSteps.toLocaleString();
    document.getElementById('totalCaloriesValue').textContent = totalCalories.toLocaleString();
    document.getElementById('avgCaloriesValue').textContent = avgCalories.toLocaleString();

    // Create steps line chart
    const stepsCtx = document.getElementById('stepsChart').getContext('2d');
    const stepsChart = new Chart(stepsCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Total Steps',
                data: steps,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                tension: 0.3,
                fill: true,
                pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Steps: ${context.raw.toLocaleString()}`;
                        }
                    }
                },
                annotation: {
                    annotations: {
                        line1: {
                            type: 'line',
                            yMin: 10000,
                            yMax: 10000,
                            borderColor: 'rgba(255, 99, 132, 0.5)',
                            borderWidth: 2,
                            borderDash: [6, 6],
                            label: {
                                content: 'Goal: 10,000 steps',
                                enabled: true,
                                position: 'end'
                            }
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Steps'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    });

    // Create calories bar chart
    const caloriesCtx = document.getElementById('caloriesChart').getContext('2d');
    const caloriesChart = new Chart(caloriesCtx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [{
                label: 'Calories Burned',
                data: calories,
                backgroundColor: 'rgba(255, 99, 132, 0.7)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
                borderRadius: 4,
                hoverBackgroundColor: 'rgba(255, 99, 132, 0.9)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Calories: ${context.raw.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Calories'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
    
    // Create activity minutes pie chart
    const activityMinutesCtx = document.getElementById('activityMinutesChart').getContext('2d');
    const avgVeryActive = Math.round(veryActiveMinutes.reduce((a, b) => a + b, 0) / veryActiveMinutes.length);
    const avgLightlyActive = Math.round(lightlyActiveMinutes.reduce((a, b) => a + b, 0) / lightlyActiveMinutes.length);
    const avgInactive = 1440 - avgVeryActive - avgLightlyActive; // 1440 minutes in a day
    
    const activityMinutesChart = new Chart(activityMinutesCtx, {
        type: 'doughnut',
        data: {
            labels: ['Very Active', 'Lightly Active', 'Inactive'],
            datasets: [{
                data: [avgVeryActive, avgLightlyActive, avgInactive],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(201, 203, 207, 0.8)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(201, 203, 207, 1)'
                ],
                borderWidth: 1,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.formattedValue || '';
                            const percentage = Math.round((context.raw / 1440) * 100);
                            return `${label}: ${value} min (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '70%'
        }
    });
    
    // Create cumulative steps area chart
    const cumulativeStepsCtx = document.getElementById('cumulativeStepsChart').getContext('2d');
    const cumulativeStepsChart = new Chart(cumulativeStepsCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Cumulative Steps',
                data: cumulativeSteps,
                borderColor: 'rgba(153, 102, 255, 1)',
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                borderWidth: 2,
                tension: 0.1,
                fill: true,
                pointBackgroundColor: 'rgba(153, 102, 255, 1)',
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Total Steps: ${context.raw.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Total Steps'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
    
    // Create distance vs. steps scatter plot
    const distanceStepsCtx = document.getElementById('distanceStepsChart').getContext('2d');
    const scatterData = fitnessData.map(entry => ({
        x: entry.steps,
        y: entry.distance
    }));
    
    const distanceStepsChart = new Chart(distanceStepsCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Steps vs. Distance',
                data: scatterData,
                backgroundColor: 'rgba(255, 159, 64, 0.7)',
                borderColor: 'rgba(255, 159, 64, 1)',
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Steps: ${context.raw.x.toLocaleString()}, Distance: ${context.raw.y} km`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Distance (km)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Steps'
                    }
                }
            }
        }
    });
    
    // Add chart filter functionality
    document.querySelectorAll('.time-filter').forEach(button => {
        button.addEventListener('click', function() {
            const days = parseInt(this.dataset.days);
            
            // Remove active class from all buttons
            document.querySelectorAll('.time-filter').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Filter data
            filterChartData(days, stepsChart, caloriesChart, cumulativeStepsChart);
        });
    });
    
    // Helper function to calculate cumulative values
    function calculateCumulative(data) {
        let sum = 0;
        return data.map(value => {
            sum += value;
            return sum;
        });
    }
    
    // Helper function to filter chart data based on time period
    function filterChartData(days, stepsChart, caloriesChart, cumulativeStepsChart) {
        if (!days || days <= 0) {
            // Show all data
            updateChartData(stepsChart, dates, steps);
            updateChartData(caloriesChart, dates, calories);
            updateChartData(cumulativeStepsChart, dates, cumulativeSteps);
            return;
        }
        
        // Filter last X days
        const filteredDates = dates.slice(-days);
        const filteredSteps = steps.slice(-days);
        const filteredCalories = calories.slice(-days);
        const filteredCumulativeSteps = calculateCumulative(filteredSteps);
        
        updateChartData(stepsChart, filteredDates, filteredSteps);
        updateChartData(caloriesChart, filteredDates, filteredCalories);
        updateChartData(cumulativeStepsChart, filteredDates, filteredCumulativeSteps);
    }
    
    // Helper function to update chart data
    function updateChartData(chart, labels, data) {
        chart.data.labels = labels;
        chart.data.datasets[0].data = data;
        chart.update();
    }

    // Chatbot functionality
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const chatContainer = document.getElementById('chat-container');
    
    // Function to add a message to the chat
    function addMessage(message, isUser = false) {
        const messageContainer = document.createElement('div');
        messageContainer.className = isUser ? 'user-message-container new-message' : 'ai-message-container new-message';
        
        const avatar = document.createElement('div');
        avatar.className = isUser ? 'user-avatar' : 'ai-avatar';
        
        const icon = document.createElement('i');
        icon.className = isUser ? 'fas fa-user' : 'fas fa-robot';
        avatar.appendChild(icon);
        
        const messageElement = document.createElement('div');
        messageElement.className = isUser ? 'user-message' : 'ai-message';
        
        if (isUser) {
            // User messages are simple text
            messageElement.textContent = message;
        } else {
            // AI messages can have formatting
            const formattedContent = document.createElement('div');
            formattedContent.className = 'formatted-content';
            formattedContent.id = 'streaming-content';
            // Convert line breaks to <br> tags and preserve formatting
            formattedContent.innerHTML = '';
            messageElement.appendChild(formattedContent);
            
            // Add typing cursor for streaming effect
            const cursor = document.createElement('span');
            cursor.className = 'typing-cursor';
            formattedContent.appendChild(cursor);
            
            // Stream the text character by character
            let index = 0;
            const messageChars = message.split('');
            
            function streamText() {
                if (index < messageChars.length) {
                    // Handle special formatting
                    if (messageChars[index] === '-' && 
                        (index === 0 || messageChars[index-1] === '\n')) {
                        // This is likely a list item
                        formattedContent.innerHTML += '• ';
                        index += 2; // Skip the hyphen and space
                    } else if (messageChars[index] === '\n') {
                        formattedContent.innerHTML += '<br>';
                        index++;
                    } else {
                        formattedContent.innerHTML += messageChars[index];
                        index++;
                    }
                    
                    // Continue streaming
                    setTimeout(streamText, 10); // Adjust speed as needed
                    
                    // Scroll to the bottom of the chat container
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                } else {
                    // Remove the cursor when done
                    cursor.remove();
                    
                    // Format any bullet points that might be in the text
                    formattedContent.innerHTML = formattedContent.innerHTML
                        .replace(/• /g, '<span style="display:inline-block;width:10px;margin-right:5px;">•</span>');
                }
            }
            
            // Start streaming
            streamText();
        }
        
        messageContainer.appendChild(avatar);
        messageContainer.appendChild(messageElement);
        
        chatMessages.appendChild(messageContainer);
        
        // Scroll to the bottom of the chat container
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Function to add typing indicator
    function addTypingIndicator() {
        const indicatorContainer = document.createElement('div');
        indicatorContainer.className = 'ai-message-container typing-indicator';
        indicatorContainer.id = 'typing-indicator';
        
        const avatar = document.createElement('div');
        avatar.className = 'ai-avatar';
        
        const icon = document.createElement('i');
        icon.className = 'fas fa-robot';
        avatar.appendChild(icon);
        
        const indicator = document.createElement('div');
        indicator.className = 'ai-message typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            indicator.appendChild(dot);
        }
        
        indicatorContainer.appendChild(avatar);
        indicatorContainer.appendChild(indicator);
        
        chatMessages.appendChild(indicatorContainer);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Function to remove typing indicator
    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    // Handle form submission
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const query = userInput.value.trim();
            if (!query) return;
            
            // Add user message to chat
            addMessage(query, true);
            
            // Clear input field
            userInput.value = '';
            
            // Show typing indicator
            addTypingIndicator();
            
            // Send request to the chatbot API
            fetch('/fit/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ user_input: query })
            })
            .then(response => response.json())
            .then(data => {
                // Remove typing indicator
                removeTypingIndicator();
                
                // Add AI response to chat
                if (data && data.suggestion) {
                    addMessage(data.suggestion);
                } else {
                    addMessage("I'm sorry, I couldn't process your request at the moment.");
                }
            })
            .catch(error => {
                console.error('Error:', error);
                removeTypingIndicator();
                addMessage("Sorry, there was an error processing your request. Please try again later.");
            });
        });
    }
    
    // Function to get CSRF token
    function getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }

    // Process initial AI suggestion to add proper formatting
    const initialSuggestion = document.getElementById('ai-suggestion');
    if (initialSuggestion) {
        const formattedContent = initialSuggestion.querySelector('.formatted-content');
        if (formattedContent) {
            // Convert bullet points in pre-formatted text
            formattedContent.innerHTML = formattedContent.innerHTML
                .replace(/- /g, '• ')
                .replace(/• /g, '<span style="display:inline-block;width:10px;margin-right:5px;">•</span>');
        }
    }
}); 