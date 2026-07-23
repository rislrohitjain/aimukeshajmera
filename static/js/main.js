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
    let itemsPerPage = 6;
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
        itemsPerPage = parseInt($('#catalog-page-size').val()) || itemsPerPage;
        const visibleCards = getVisibleCards();
        const totalItems = visibleCards.length;
        const totalPages = Math.ceil(totalItems / itemsPerPage) || 1;

        if (currentPage > totalPages) currentPage = 1;

        // Hide all cards first
        $('.product-card').addClass('hidden');

        // Show slice for current page
        const startIdx = (currentPage - 1) * itemsPerPage;
        const endIdx = startIdx + itemsPerPage;

        visibleCards.slice(startIdx, endIdx).removeClass('hidden');

        // Render Pagination Controls HTML with page size selector!
        let paginationHTML = '<div class="flex flex-col sm:flex-row items-center justify-between gap-4 border border-slate-200 dark:border-slate-800 p-3 rounded-2xl bg-white dark:bg-slate-900 shadow-sm text-xs font-semibold w-full sm:w-auto">';
        
        paginationHTML += `
            <div class="flex items-center gap-2">
                <span class="text-slate-500 font-bold">प्रति पृष्ठ योजनाएं (Show Rows):</span>
                <select id="catalog-page-size" class="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 font-bold text-slate-900 dark:text-white outline-none">
                    <option value="2" ${itemsPerPage === 2 ? 'selected' : ''}>2 per page</option>
                    <option value="5" ${itemsPerPage === 5 ? 'selected' : ''}>5 per page</option>
                    <option value="6" ${itemsPerPage === 6 ? 'selected' : ''}>6 per page</option>
                    <option value="10" ${itemsPerPage === 10 ? 'selected' : ''}>10 per page</option>
                    <option value="100" ${itemsPerPage === 100 ? 'selected' : ''}>100 per page</option>
                    <option value="1000" ${itemsPerPage === 1000 ? 'selected' : ''}>1000 per page</option>
                </select>
            </div>
        `;

        if (totalPages > 1) {
            paginationHTML += '<div class="flex items-center gap-1.5 overflow-x-auto max-w-full">';
            paginationHTML += `<button id="plan-prev-btn" class="px-3.5 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-bold hover:bg-blue-600 hover:text-white transition ${currentPage === 1 ? 'opacity-50 cursor-not-allowed' : ''}"><i class="fas fa-chevron-left mr-1"></i> पिछले</button>`;

            for (let i = 1; i <= totalPages; i++) {
                const isActive = (i === currentPage);
                paginationHTML += `<button data-page="${i}" class="plan-page-num w-8 h-8 rounded-xl font-bold transition ${isActive ? 'bg-blue-600 text-white shadow-md' : 'bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-blue-500'}">${i}</button>`;
            }

            paginationHTML += `<button id="plan-next-btn" class="px-3.5 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-bold hover:bg-blue-600 hover:text-white transition ${currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : ''}">अगले <i class="fas fa-chevron-right ml-1"></i></button>`;
            paginationHTML += '</div>';
        }

        paginationHTML += '</div>';

        $('#plan-pagination-controls').html(paginationHTML);
    }

    $(document).on('change', '#catalog-page-size', function() {
        currentPage = 1;
        renderPagination();
    });

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

// Global Excel Exporter using SheetJS / CSV Fallback
function exportTableToExcel(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) {
        alert('Table not found for export.');
        return;
    }
    
    filename = filename || (tableId + '_export.xlsx');
    
    if (typeof XLSX !== 'undefined') {
        const wb = XLSX.utils.table_to_book(table, { sheet: "Data" });
        XLSX.writeFile(wb, filename);
    } else {
        // Fallback CSV Generator
        let csv = [];
        const rows = table.querySelectorAll("tr");
        for (let i = 0; i < rows.length; i++) {
            let row = [];
            let cols = rows[i].querySelectorAll("td, th");
            for (let j = 0; j < cols.length; j++) {
                let cellText = cols[j].innerText.replace(/"/g, '""').replace(/\s+/g, ' ').trim();
                row.push('"' + cellText + '"');
            }
            csv.push(row.join(","));
        }
        const csvBlob = new Blob([csv.join("\n")], { type: "text/csv;charset=utf-8;" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(csvBlob);
        link.setAttribute("download", filename.replace('.xlsx', '.csv'));
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Universal Client-Side Table Paginator (Supports 2, 5, 10, 100, 1000 items per page & page numbers)
function initTablePagination(tableId, pageSizeSelectId, infoId, prevBtnId, nextBtnId, numbersContainerId) {
    const $table = $('#' + tableId);
    if (!$table.length) return;

    let currentPage = 1;
    let pageSize = parseInt($('#' + pageSizeSelectId).val()) || 10;

    function renderTablePage() {
        $table.find('tbody tr.filtered-out').addClass('hidden');
        const $rows = $table.find('tbody tr:not(.filtered-out)');
        const totalRows = $rows.length;
        if (totalRows === 0) {
            $('#' + infoId).text('No records found');
            $('#' + prevBtnId).prop('disabled', true);
            $('#' + nextBtnId).prop('disabled', true);
            if (numbersContainerId && $('#' + numbersContainerId).length) {
                $('#' + numbersContainerId).empty();
            }
            return;
        }

        const totalPages = Math.ceil(totalRows / pageSize) || 1;
        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;

        const startIndex = (currentPage - 1) * pageSize;
        const endIndex = startIndex + pageSize;

        $rows.each(function(index) {
            if (index >= startIndex && index < endIndex) {
                $(this).removeClass('hidden');
            } else {
                $(this).addClass('hidden');
            }
        });

        const dispEnd = Math.min(endIndex, totalRows);
        $('#' + infoId).html(`Page <strong>${currentPage}</strong> of <strong>${totalPages}</strong> (Showing ${startIndex + 1}-${dispEnd} of ${totalRows})`);

        $('#' + prevBtnId).prop('disabled', currentPage === 1);
        $('#' + nextBtnId).prop('disabled', currentPage >= totalPages);

        if (numbersContainerId && $('#' + numbersContainerId).length) {
            let numHtml = '';
            for (let i = 1; i <= totalPages; i++) {
                const activeCls = (i === currentPage) ? 'bg-emerald-600 text-white font-bold shadow' : 'bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 hover:bg-emerald-500 hover:text-white';
                numHtml += `<button data-page="${i}" class="table-page-num-btn px-2.5 py-1 rounded-lg text-xs font-bold transition ${activeCls}">${i}</button>`;
            }
            $('#' + numbersContainerId).html(numHtml);
        }
    }

    if (numbersContainerId) {
        $(document).off('click', '#' + numbersContainerId + ' .table-page-num-btn').on('click', '#' + numbersContainerId + ' .table-page-num-btn', function() {
            currentPage = parseInt($(this).data('page'));
            renderTablePage();
        });
    }

    $('#' + pageSizeSelectId).off('change.tblpag').on('change.tblpag', function() {
        pageSize = parseInt($(this).val()) || 10;
        currentPage = 1;
        renderTablePage();
    });

    $('#' + prevBtnId).off('click.tblpag').on('click.tblpag', function() {
        if (currentPage > 1) {
            currentPage--;
            renderTablePage();
        }
    });

    $('#' + nextBtnId).off('click.tblpag').on('click.tblpag', function() {
        const totalRows = $table.find('tbody tr').length;
        const totalPages = Math.ceil(totalRows / pageSize) || 1;
        if (currentPage < totalPages) {
            currentPage++;
            renderTablePage();
        }
    });

    renderTablePage();
}

// Universal Table Search & Category Filter Engine
function initTableFilter(tableId, searchInputId, dropdownSelectors, onFilterCallback) {
    const $table = $('#' + tableId);
    if (!$table.length) return;

    function filterRows() {
        const query = ($('#' + searchInputId).val() || '').toLowerCase().trim();

        $table.find('tbody tr').each(function() {
            const $row = $(this);
            const rowText = $row.text().toLowerCase();
            let showRow = true;

            if (query && rowText.indexOf(query) === -1) {
                showRow = false;
            }

            if (showRow && dropdownSelectors && dropdownSelectors.length) {
                dropdownSelectors.forEach(function(sel) {
                    const filterVal = ($(sel).val() || '').toLowerCase().trim();
                    if (filterVal && filterVal !== 'all') {
                        if (rowText.indexOf(filterVal) === -1) {
                            showRow = false;
                        }
                    }
                });
            }

            if (showRow) {
                $row.removeClass('filtered-out');
            } else {
                $row.addClass('filtered-out hidden');
            }
        });

        if (typeof onFilterCallback === 'function') {
            onFilterCallback();
        }
    }

    $('#' + searchInputId).on('keyup input', filterRows);
    if (dropdownSelectors && dropdownSelectors.length) {
        dropdownSelectors.forEach(function(sel) {
            $(sel).on('change', filterRows);
        });
    }
}

