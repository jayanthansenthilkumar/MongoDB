$(document).ready(function() {
    try {
        // Initialize a clean DataTable with a modern look
        if ($.fn.DataTable.isDataTable('#allDocsTable')) {
            $('#allDocsTable').DataTable().destroy();
        }
        
        // Show loading indicator
        $('#tableLoading').show();
        
        // Initialize DataTable with simplified configuration
        const table = $('#allDocsTable').DataTable({
            responsive: true,
            pageLength: 10,
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
            searching: true,
            ordering: true,
            info: true,
            autoWidth: true, // Changed to true for better fitting
            scrollY: '100%', // Make it use available height
            scrollCollapse: true,
            paging: true,
            language: {
                search: "",
                searchPlaceholder: "Search documents...",
                lengthMenu: "_MENU_",
                info: "Showing _START_ to _END_ of _TOTAL_ documents",
                infoEmpty: "No documents found",
                infoFiltered: "(filtered from _MAX_ total records)",
                zeroRecords: "No matching documents found"
            },
            dom: '<"top"<"dataTables_length_container"l><"dataTables_filter_container"f>><"table-responsive"rt><"bottom"i>',
            initComplete: function() {
                // Hide loading when complete
                $('#tableLoading').hide();
                
                // Enhanced search input
                $('.dataTables_filter input')
                    .attr('placeholder', 'Search documents...')
                    .addClass('search-input');
                
                // Add search icon
                $('.dataTables_filter label').prepend('<i class="fas fa-search"></i>');
                
                // Add clear button for search
                $('.dataTables_filter label').append('<span class="search-clear"><i class="fas fa-times"></i></span>');
                
                // Clear search functionality
                $('.search-clear').click(function() {
                    $('.dataTables_filter input').val('').trigger('input');
                    $(this).hide();
                });
                
                // Show/hide clear button based on search content
                $('.dataTables_filter input').on('input', function() {
                    if ($(this).val().length > 0) {
                        $('.search-clear').show();
                    } else {
                        $('.search-clear').hide();
                    }
                });
                
                // Enhanced "Show entries" dropdown
                $('.dataTables_length label').contents().filter(function() {
                    return this.nodeType === 3;
                }).remove();
                
                $('.dataTables_length select').before('<span class="entries-label">Show</span>');
                $('.dataTables_length select').after('<span class="entries-label">entries</span>');
                
                // Adjust table to fit available space
                $(window).trigger('resize');
                
                // Make sure the table fills the container
                $('.dataTables_scrollBody').css('flex', '1');
            }
        });
        
        // Add resize handler to adjust table when window changes size
        $(window).on('resize', function() {
            // Calculate available height
            const topBarHeight = $('.top-bar').outerHeight() || 0;
            const statsGridHeight = $('.stats-grid').outerHeight() || 0;
            const sectionTitleHeight = $('.section-title').outerHeight() || 0;
            const sectionHeaderHeight = $('.section-header').outerHeight() || 0;
            const tableControlsHeight = $('.dataTables_length').outerHeight() + 20 || 0;
            
            const availableHeight = window.innerHeight - (
                topBarHeight + 
                statsGridHeight + 
                sectionTitleHeight + 
                sectionHeaderHeight + 
                tableControlsHeight +
                80 // Additional padding/margins
            );
            
            // Apply height to the scrollable area
            if (availableHeight > 200) { // Ensure minimum reasonable height
                $('.dataTables_scrollBody').css('max-height', availableHeight + 'px');
            }
        });
        
        // Trigger resize on load
        setTimeout(function() {
            $(window).trigger('resize');
        }, 100);
        
        // Connect global search to DataTable
        $('.global-search').on('keyup', function() {
            table.search(this.value).draw();
        });
        
        // Add export functionality with better UX
        $('.action-btn').click(function() {
            $(this).prop('disabled', true);
            $(this).html('<i class="fas fa-spinner fa-spin"></i> Exporting...');
            
            setTimeout(() => {
                try {
                    // Get data from all rows (not just visible ones)
                    const data = [];
                    table.rows().every(function() {
                        data.push(Object.values(this.data()));
                    });
                    
                    // Get column headers
                    const headers = [];
                    table.columns().header().each(function(h) {
                        headers.push($(h).text());
                    });
                    
                    // Generate CSV
                    const csv = [
                        headers.join(','),
                        ...data.map(row => row.join(','))
                    ].join('\n');
                    
                    // Download file
                    const blob = new Blob([csv], { type: 'text/csv' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `mongodb_export_${new Date().toISOString().split('T')[0]}.csv`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } catch(err) {
                    console.error('Export failed:', err);
                    alert('Export failed. See console for details.');
                }
                
                // Reset button
                $(this).prop('disabled', false);
                $(this).html('<i class="fas fa-download"></i> Export');
            }, 500);
        });
        
        // Refresh button animation
        $('.refresh-btn').click(function() {
            $(this).addClass('rotating');
        });
        
    } catch(err) {
        console.error('DataTable initialization failed:', err);
        $('#tableLoading').hide();
    }
});

// Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Refresh button functionality
    const refreshBtn = document.querySelector('.refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            location.reload();
        });
    }

    // Handle global search
    const globalSearch = document.querySelector('.global-search');
    if (globalSearch) {
        globalSearch.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                // Focus the DataTables search input and trigger the search
                const dtSearchInput = document.querySelector('.dataTables_filter input');
                if (dtSearchInput) {
                    dtSearchInput.value = this.value;
                    dtSearchInput.dispatchEvent(new Event('input'));
                    dtSearchInput.focus();
                }
            }
        });
    }

    // Handle export button
    const exportBtn = document.querySelector('.action-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            alert('Export functionality will be implemented here');
            // Future implementation can include CSV or JSON export
        });
    }
    
    // Help button functionality
    const helpBtn = document.querySelector('.btn-help');
    if (helpBtn) {
        helpBtn.addEventListener('click', function() {
            alert('MongoDB Dashboard Help\n\n• Use the sidebar to navigate between sections\n• Search for documents using the search box\n• Export data using the Export button\n• View detailed statistics in the Analytics section');
        });
    }
    
    // Welcome card buttons functionality
    const docBtn = document.querySelector('.welcome-actions .welcome-btn:first-child');
    if (docBtn) {
        docBtn.addEventListener('click', function() {
            window.open('https://www.mongodb.com/docs/', '_blank');
        });
    }
    
    const tutorialBtn = document.querySelector('.welcome-actions .welcome-btn:last-child');
    if (tutorialBtn) {
        tutorialBtn.addEventListener('click', function() {
            window.open('https://university.mongodb.com/', '_blank');
        });
    }
    
    // Display current date in header
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dateDisplay = document.querySelector('.date-display');
    if (dateDisplay) {
        dateDisplay.textContent = now.toLocaleDateString('en-US', options);
    }
    
    // Add smooth scrolling for navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const targetSection = document.querySelector(href);
                if (targetSection) {
                    targetSection.scrollIntoView({ behavior: 'smooth' });
                }
                
                // Update active nav link
                document.querySelectorAll('.nav-link').forEach(navLink => {
                    navLink.classList.remove('active');
                });
                this.classList.add('active');
            }
        });
    });

    // Adjust table size calculation to account for new header
    $(window).on('resize', function() {
        // Calculate available height with new header
        const enhancedHeaderHeight = $('.enhanced-header').outerHeight() || 0;
        const welcomeCardHeight = $('.welcome-card').outerHeight() || 0;
        const statsGridHeight = $('.stats-grid').outerHeight() || 0;
        const sectionHeaderHeight = $('.section-header').outerHeight() || 0;
        const tableControlsHeight = $('.dataTables_length').outerHeight() + 20 || 0;
        
        const availableHeight = window.innerHeight - (
            enhancedHeaderHeight + 
            welcomeCardHeight +
            statsGridHeight + 
            sectionHeaderHeight + 
            tableControlsHeight +
            60 // Additional padding/margins
        );
        
        // Apply height to the scrollable area
        if (availableHeight > 200) { // Ensure minimum reasonable height
            $('.dataTables_scrollBody').css('max-height', availableHeight + 'px');
        }
    });

    // Update current date format to include time
    const updateDateTime = function() {
        const now = new Date();
        // More compact date format
        const options = { 
            weekday: 'short', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        const dateDisplay = document.querySelector('.date-display');
        if (dateDisplay) {
            dateDisplay.textContent = now.toLocaleDateString('en-US', options);
        }
    };
    
    // Update date/time immediately and then every minute
    updateDateTime();
    setInterval(updateDateTime, 60000);
    
    // User profile dropdown functionality
    const userProfile = document.querySelector('.user-profile');
    if (userProfile) {
        // Toggle dropdown on click
        userProfile.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent document click from closing it
            userProfile.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!userProfile.contains(e.target)) {
                userProfile.classList.remove('active');
            }
        });
        
        // Status button functionality
        document.querySelectorAll('.status-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation(); // Prevent dropdown from closing
                
                // Remove active class from all buttons
                document.querySelectorAll('.status-btn').forEach(b => {
                    b.classList.remove('active');
                });
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Get status from data attribute
                const status = this.getAttribute('data-status');
                updateUserStatus(status);
                
                // Update status text in dropdown header
                const statusText = status.charAt(0).toUpperCase() + status.slice(1);
                const statusEl = document.querySelector('.user-status');
                if (statusEl) {
                    statusEl.innerHTML = `<i class="fas fa-circle"></i> ${statusText}`;
                }
            });
        });
    }
    
    // Update the updateUserStatus function to update status colors more comprehensively
    function updateUserStatus(status) {
        const indicator = document.querySelector('.status-indicator');
        
        if (indicator) {
            // Remove all status classes
            indicator.classList.remove('active', 'away', 'offline');
            // Add the current status class
            indicator.classList.add(status);
            
            // Update status icon color in the dropdown
            const statusIcon = document.querySelector('.user-status i');
            if (statusIcon) {
                statusIcon.style.color = 
                    status === 'active' ? 'var(--color-success)' :
                    status === 'away' ? 'var(--color-warning)' :
                    'var(--color-text-muted)';
            }
            
            // Update status pill background color
            const statusPill = document.querySelector('.user-status');
            if (statusPill) {
                statusPill.style.background = 
                    status === 'active' ? 'rgba(16, 185, 129, 0.2)' :
                    status === 'away' ? 'rgba(245, 158, 11, 0.2)' :
                    'rgba(107, 114, 128, 0.2)';
            }
        }
    }
    
    // Keep the inactivity timer but update the dropdown status as well
    let inactivityTimer;
    
    function resetInactivityTimer() {
        clearTimeout(inactivityTimer);
        updateUserStatus('active');
        
        // Update status button active state
        document.querySelectorAll('.status-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-status') === 'active') {
                btn.classList.add('active');
            }
        });
        
        // Update status text
        const statusEl = document.querySelector('.user-status');
        if (statusEl) {
            statusEl.innerHTML = '<i class="fas fa-circle"></i> Active';
        }
        
        inactivityTimer = setTimeout(() => {
            updateUserStatus('away');
            
            // Update status button active state
            document.querySelectorAll('.status-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.getAttribute('data-status') === 'away') {
                    btn.classList.add('active');
                }
            });
            
            // Update status text
            const statusEl = document.querySelector('.user-status');
            if (statusEl) {
                statusEl.innerHTML = '<i class="fas fa-circle"></i> Away';
            }
            
        }, 5 * 60 * 1000); // 5 minutes
    }
    
    // Reset timer on user activity
    ['mousemove', 'keydown', 'mousedown', 'touchstart'].forEach(event => {
        document.addEventListener(event, resetInactivityTimer);
    });
    
    // Initialize timer
    resetInactivityTimer();
});
