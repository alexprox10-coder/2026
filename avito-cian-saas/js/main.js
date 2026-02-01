// ========================================
// Avito-Cian Parser SaaS - Main JavaScript
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initNavbar();
    initAOS();
    initPricingToggle();
    initFAQ();
    initChatWidget();
    initMobileMenu();
});

// Navbar scroll effect
function initNavbar() {
    const navbar = document.getElementById('navbar');

    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// AOS-like scroll animations
function initAOS() {
    const animatedElements = document.querySelectorAll('[data-aos]');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Add delay if specified
                const delay = entry.target.dataset.aosDelay || 0;
                setTimeout(() => {
                    entry.target.classList.add('aos-animate');
                }, delay);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    animatedElements.forEach(el => observer.observe(el));
}

// Pricing toggle (monthly/yearly)
function initPricingToggle() {
    const toggle = document.getElementById('pricingToggle');
    const monthlyLabel = document.querySelector('[data-period="monthly"]');
    const yearlyLabel = document.querySelector('[data-period="yearly"]');
    const priceAmounts = document.querySelectorAll('.price-amount');

    if (!toggle) return;

    toggle.addEventListener('change', function() {
        const isYearly = this.checked;

        // Toggle active labels
        monthlyLabel.classList.toggle('active', !isYearly);
        yearlyLabel.classList.toggle('active', isYearly);

        // Update prices
        priceAmounts.forEach(amount => {
            const monthly = amount.dataset.monthly;
            const yearly = amount.dataset.yearly;

            if (monthly !== undefined && yearly !== undefined) {
                amount.textContent = isYearly ? formatPrice(yearly) : formatPrice(monthly);
            }
        });
    });
}

// Format price with spaces
function formatPrice(price) {
    return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

// FAQ accordion
function initFAQ() {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');

        question.addEventListener('click', () => {
            // Close other items
            faqItems.forEach(other => {
                if (other !== item) {
                    other.classList.remove('active');
                }
            });

            // Toggle current item
            item.classList.toggle('active');
        });
    });
}

// Chat widget
function initChatWidget() {
    const chatBtn = document.getElementById('chatBtn');
    const chatPopup = document.getElementById('chatPopup');
    const chatClose = document.getElementById('chatClose');

    if (!chatBtn || !chatPopup) return;

    chatBtn.addEventListener('click', () => {
        chatPopup.classList.toggle('active');
    });

    chatClose.addEventListener('click', () => {
        chatPopup.classList.remove('active');
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.chat-widget')) {
            chatPopup.classList.remove('active');
        }
    });
}

// Mobile menu
function initMobileMenu() {
    const menuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');

    if (!menuBtn) return;

    menuBtn.addEventListener('click', () => {
        menuBtn.classList.toggle('active');
        navLinks.classList.toggle('active');
    });
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#') return;

        e.preventDefault();
        const target = document.querySelector(href);

        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Typing effect for hero (optional)
function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.textContent = '';

    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }

    type();
}

// Counter animation
function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = formatPrice(target);
            clearInterval(timer);
        } else {
            element.textContent = formatPrice(Math.floor(current));
        }
    }, 16);
}

// Initialize counters when visible
const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const target = parseInt(entry.target.dataset.count);
            animateCounter(entry.target, target);
            counterObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('[data-count]').forEach(el => {
    counterObserver.observe(el);
});

// Form validation helper
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Export functions for use in other modules
window.ParserSaaS = {
    showNotification,
    validateEmail,
    formatPrice
};
