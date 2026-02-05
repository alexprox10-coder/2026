document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    const navActions = document.querySelector('.nav-actions');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            navActions.classList.toggle('active');
        });
    }

    // FAQ Accordion
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(function(item) {
        const question = item.querySelector('.faq-question');
        if (question) {
            question.addEventListener('click', function() {
                const isActive = item.classList.contains('active');
                faqItems.forEach(function(i) {
                    i.classList.remove('active');
                });
                if (!isActive) {
                    item.classList.add('active');
                }
            });
        }
    });

    // Chat Widget
    const chatBtn = document.querySelector('.chat-btn');
    const chatPopup = document.querySelector('.chat-popup');
    const chatClose = document.querySelector('.chat-close');

    if (chatBtn && chatPopup) {
        chatBtn.addEventListener('click', function() {
            chatPopup.classList.toggle('active');
        });
        
        if (chatClose) {
            chatClose.addEventListener('click', function() {
                chatPopup.classList.remove('active');
            });
        }
    }

    // Pricing Toggle
    const toggleSwitch = document.querySelector('.toggle-switch input');
    const monthlyLabel = document.querySelector('.toggle-label:first-child');
    const yearlyLabel = document.querySelector('.toggle-label:last-child');

    if (toggleSwitch && monthlyLabel && yearlyLabel) {
        toggleSwitch.addEventListener('change', function() {
            if (toggleSwitch.checked) {
                monthlyLabel.classList.remove('active');
                yearlyLabel.classList.add('active');
            } else {
                monthlyLabel.classList.add('active');
                yearlyLabel.classList.remove('active');
            }
        });
    }

    // Simple AOS (Animate On Scroll)
    function animateOnScroll() {
        const elements = document.querySelectorAll('[data-aos]');
        elements.forEach(function(el) {
            const rect = el.getBoundingClientRect();
            const windowHeight = window.innerHeight;
            if (rect.top < windowHeight - 100) {
                el.classList.add('aos-animate');
            }
        });
    }

    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll();

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                const target = document.querySelector(targetId);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});
