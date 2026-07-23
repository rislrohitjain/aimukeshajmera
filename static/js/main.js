// Main Application JavaScript for Mukesh Ajmera LIC & Post Office

$(document).ready(function() {
    // 1. Theme Switcher Logic
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    $('#theme-toggle-btn').on('click', function() {
        const currentTheme = $('html').attr('data-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });

    function setTheme(theme) {
        $('html').attr('data-theme', theme);
        localStorage.setItem('theme', theme);
        if (theme === 'dark') {
            $('#theme-icon').removeClass('fa-moon').addClass('fa-sun');
            $('#theme-text').text('Light Mode');
        } else {
            $('#theme-icon').removeClass('fa-sun').addClass('fa-moon');
            $('#theme-text').text('Dark Mode');
        }
    }

    // 2. Animated Smooth Scroll for Menu Links
    $('a[href^="#"]').on('click', function(e) {
        const target = $(this.getAttribute('href'));
        if (target.length) {
            e.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 80
            }, 600);
            $('#mobile-menu').addClass('hidden');
        }
    });

    // 3. PRODUCT CATALOG PAGINATION & ACTIVE FILTER COLOR SYSTEM
    const ITEMS_PER_PAGE = 6;
    let currentCategory = 'all';
    let currentPage = 1;

    function getVisibleCards() {
        if (currentCategory === 'all') {
            return $('.product-card');
        } else {
            return $(`.product-card[data-category="${currentCategory}"]`);
        }
    }

    function renderPagination() {
        const visibleCards = getVisibleCards();
        const totalItems = visibleCards.length;
        const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE) || 1;

        if (currentPage > totalPages) currentPage = 1;

        // Hide all cards first
        $('.product-card').addClass('hidden');

        // Show slice for current page
        const startIdx = (currentPage - 1) * ITEMS_PER_PAGE;
        const endIdx = startIdx + ITEMS_PER_PAGE;

        visibleCards.slice(startIdx, endIdx).removeClass('hidden');

        // Render Pagination Buttons
        let paginationHTML = '';

        if (totalPages > 1) {
            // Prev Button
            paginationHTML += `<button id="plan-prev-btn" class="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-bold text-xs hover:bg-blue-600 hover:text-white transition ${currentPage === 1 ? 'opacity-50 cursor-not-allowed' : ''}"><i class="fas fa-chevron-left mr-1"></i> पिछले</button>`;

            // Page Number Pills
            for (let i = 1; i <= totalPages; i++) {
                const isActive = (i === currentPage);
                paginationHTML += `<button data-page="${i}" class="plan-page-num w-9 h-9 rounded-xl font-bold text-xs transition ${isActive ? 'bg-blue-600 text-white shadow-md' : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-blue-500'}">${i}</button>`;
            }

            // Next Button
            paginationHTML += `<button id="plan-next-btn" class="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-bold text-xs hover:bg-blue-600 hover:text-white transition ${currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : ''}">अगले <i class="fas fa-chevron-right ml-1"></i></button>`;
        }

        $('#plan-pagination-controls').html(paginationHTML);
    }

    // Filter Tab Button Click Handler (Active Color Highlight)
    $('.filter-btn').on('click', function() {
        // Reset all filter buttons to neutral style
        $('.filter-btn')
            .removeClass('bg-blue-600 text-white shadow-lg ring-2 ring-blue-400')
            .addClass('bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700');

        // Apply Active Color to Clicked Button
        $(this)
            .removeClass('bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700')
            .addClass('bg-blue-600 text-white shadow-lg ring-2 ring-blue-400');

        currentCategory = $(this).data('category');
        currentPage = 1;

        // Show Skeleton Shimmer Loading Simulation
        $('#product-skeleton-grid').removeClass('hidden');
        $('#product-real-grid').addClass('hidden');

        setTimeout(function() {
            $('#product-skeleton-grid').addClass('hidden');
            $('#product-real-grid').removeClass('hidden');
            renderPagination();
        }, 250);
    });

    // Pagination Click Event Delegation
    $(document).on('click', '.plan-page-num', function() {
        currentPage = parseInt($(this).data('page'));
        renderPagination();
        $('html, body').animate({ scrollTop: $('#plans').offset().top - 80 }, 400);
    });

    $(document).on('click', '#plan-prev-btn', function() {
        if (currentPage > 1) {
            currentPage--;
            renderPagination();
            $('html, body').animate({ scrollTop: $('#plans').offset().top - 80 }, 400);
        }
    });

    $(document).on('click', '#plan-next-btn', function() {
        const totalPages = Math.ceil(getVisibleCards().length / ITEMS_PER_PAGE);
        if (currentPage < totalPages) {
            currentPage++;
            renderPagination();
            $('html, body').animate({ scrollTop: $('#plans').offset().top - 80 }, 400);
        }
    });

    // Initial Pagination Render on Page Load
    renderPagination();

    // 4. Content Protection Right-Click Security Toast
    $(document).on('contextmenu', function(e) {
        e.preventDefault();
        showSecurityToast('🔒 Content Protected: Right-click is disabled on Mukesh Ajmera LIC Portal.');
    });

    function showSecurityToast(msg) {
        $('#toast-message').text(msg);
        const toast = $('#security-toast');
        toast.addClass('show');
        setTimeout(function() { toast.removeClass('show'); }, 3000);
    }

    // 5. Mobile Menu Toggle
    $('#mobile-menu-btn').on('click', function() {
        $('#mobile-menu').toggleClass('hidden');
    });

    // 6. Voice Input for Contact Form Fields
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const contactRec = new SpeechRecognition();
        contactRec.lang = 'hi-IN';

        $('#contact-voice-btn').on('click', function() {
            contactRec.start();
            $(this).addClass('text-red-500 animate-pulse');
        });

        contactRec.onresult = function(e) {
            const text = e.results[0][0].transcript;
            $('#contact_message').val(text);
            $('#contact-voice-btn').removeClass('text-red-500 animate-pulse');
        };

        contactRec.onend = function() {
            $('#contact-voice-btn').removeClass('text-red-500 animate-pulse');
        };
    }
});

// Global External Link Handler for Social Media & External Portals
function ExternalLink(url) {
    if (url) {
        window.open(url, '_blank', 'noopener,noreferrer');
    }
}

