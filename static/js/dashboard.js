// static/js/dashboard.js
// Real-time updates and interactions

class Dashboard {
    constructor() {
        this.initializeEventListeners();
        this.startRealTimeUpdates();
    }

    initializeEventListeners() {
        // Auto-refresh functionality
        const refreshButtons = document.querySelectorAll('[data-refresh]');
        refreshButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const target = e.target.dataset.refresh;
                this.refreshComponent(target);
            });
        });

        // Modal triggers
        const modalTriggers = document.querySelectorAll('[data-modal]');
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                const modalId = e.target.dataset.modal;
                this.showModal(modalId);
            });
        });
    }

    startRealTimeUpdates() {
        // Update recommendations every 5 minutes
        setInterval(() => {
            this.updateRecommendations();
        }, 300000);

        // Update analytics every 10 minutes
        setInterval(() => {
            this.updateAnalytics();
        }, 600000);
    }

    async updateRecommendations() {
        try {
            const customerId = this.getCurrentCustomerId();
            if (!customerId) return;

            const response = await fetch(`/api/recommendations/${customerId}`);
            const recommendations = await response.json();
            
            this.renderRecommendations(recommendations);
        } catch (error) {
            console.error('Failed to update recommendations:', error);
        }
    }

    async updateAnalytics() {
        try {
            const response = await fetch('/api/segmentation/update');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification('Analytics updated successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to update analytics:', error);
        }
    }

    getCurrentCustomerId() {
        const element = document.querySelector('[data-customer-id]');
        return element ? element.dataset.customerId : null;
    }

    renderRecommendations(recommendations) {
        const container = document.getElementById('recommendations-container');
        if (!container) return;

        container.innerHTML = recommendations.map(rec => `
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h6>${rec.name}</h6>
                        <p class="text-muted">${rec.category}</p>
                        <strong>$${rec.price.toFixed(2)}</strong>
                    </div>
                </div>
            </div>
        `).join('');
    }

    showNotification(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.querySelector('main').prepend(alert);
        
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    refreshComponent(componentName) {
        const button = document.querySelector(`[data-refresh="${componentName}"]`);
        if (button) {
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            setTimeout(() => {
                location.reload();
            }, 1000);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Export functions for global use
window.Dashboard = Dashboard;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;