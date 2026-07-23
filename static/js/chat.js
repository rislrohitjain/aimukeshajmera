// AI Chatbot Handler for "LIC MITRA" / Mukesh Ajmera AI

$(document).ready(function() {
    // Open / Close / Min / Max / End Chatbot Window
    $('#chat-toggle-btn').on('click', function() {
        $('#chat-widget-window').toggleClass('hidden');
        if (!$('#chat-widget-window').hasClass('hidden')) {
            $('#chat-input').focus();
        }
    });

    $('#chat-close-btn').on('click', function() {
        $('#chat-widget-window').addClass('hidden');
    });

    $('#chat-min-btn').on('click', function() {
        $('#chat-widget-window').addClass('hidden');
    });

    $('#chat-max-btn').on('click', function() {
        const $w = $('#chat-widget-window');
        if ($w.hasClass('h-[80vh]')) {
            $w.removeClass('h-[80vh] sm:w-[600px]').addClass('h-[540px] sm:w-[400px]');
            $(this).find('i').removeClass('fa-window-restore').addClass('fa-window-maximize');
        } else {
            $w.removeClass('h-[540px] sm:w-[400px]').addClass('h-[80vh] sm:w-[600px]');
            $(this).find('i').removeClass('fa-window-maximize').addClass('fa-window-restore');
        }
    });

    $('#chat-end-btn').on('click', function() {
        if (confirm('क्या आप यह चैट सत्र समाप्त (End Chat) करके नया चैट शुरू करना चाहते हैं?')) {
            $('#chat-messages').find('.flex:gt(0)').remove();
            $('#chat-input').val('');
        }
    });

    // Global Interactive Option Click Handler (HDFC / PolicyBazaar Style)
    window.sendOptionQuery = function(queryText) {
        if ($('#chat-widget-window').hasClass('hidden')) {
            $('#chat-widget-window').removeClass('hidden');
        }
        $('#chat-input').val(queryText);
        sendMessage();
    };

    // Handle Quick Prompt Chips
    $(document).on('click', '.quick-chip', function() {
        const text = $(this).text().replace(/^[^\w\s\u0900-\u097F]+/, '').trim();
        $('#chat-input').val(text);
        sendMessage();
    });

    // Send Message on Button Click or Enter
    $('#chat-send-btn').on('click', function() {
        sendMessage();
    });

    $('#chat-input').on('keypress', function(e) {
        if (e.which === 13) {
            sendMessage();
        }
    });

    function sendMessage() {
        const message = $('#chat-input').val().trim();
        if (!message) return;

        // Append User Message
        appendUserMessage(message);
        $('#chat-input').val('');

        // Show Typing Indicator
        showTypingIndicator();

        // Send AJAX request
        $.ajax({
            url: '/api/chat',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: message }),
            success: function(response) {
                hideTypingIndicator();
                appendAIMessage(response.response, response.whatsapp_url, response.matched_plan, response.confidence_score);
            },
            error: function(xhr) {
                hideTypingIndicator();
                appendAIMessage("Forgive us, a connection error occurred. Please contact Mukesh Ajmera directly on WhatsApp (+91 98299 43216).", "https://wa.me/919829943216?text=Hi%20Mukesh%20Ji,%20I%20need%20assistance.", "Support", "95%");
            }
        });
    }

    function appendUserMessage(text) {
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const html = `
            <div class="flex justify-end mb-3">
                <div class="bg-blue-600 text-white p-3 rounded-2xl rounded-tr-none max-w-[85%] text-sm shadow">
                    <div>${escapeHtml(text)}</div>
                    <div class="text-[10px] text-blue-200 text-right mt-1 opacity-80">${timeStr}</div>
                </div>
            </div>
        `;
        $('#chat-messages').append(html);
        scrollToBottom();
    }

    function appendAIMessage(text, whatsappUrl, matchedPlan, confidenceScore) {
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const score = confidenceScore || '96%';

        // Convert line breaks and bold formatting
        let formattedText = text.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        let ctaButtonHtml = '';
        if (whatsappUrl) {
            ctaButtonHtml = `
                <div class="mt-3 pt-2 border-t border-gray-200 dark:border-gray-700 flex flex-wrap items-center justify-between gap-2">
                    <a href="${whatsappUrl}" target="_blank" rel="noopener" class="inline-flex items-center px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow transition transform hover:-translate-y-0.5">
                        <i class="fab fa-whatsapp text-sm mr-1.5"></i>
                        Mukesh Ajmera WhatsApp
                    </a>
                    <button onclick="speakText(this)" data-text="${escapeHtml(text.replace(/<[^>]*>?/gm, ''))}" class="p-1.5 text-xs text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/40 rounded-lg transition" title="Speak Response (Text to Speech)">
                        <i class="fas fa-volume-up"></i> Voice Output
                    </button>
                </div>
            `;
        } else {
            ctaButtonHtml = `
                <div class="mt-2 text-right">
                    <button onclick="speakText(this)" data-text="${escapeHtml(text.replace(/<[^>]*>?/gm, ''))}" class="p-1.5 text-xs text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/40 rounded-lg transition" title="Speak Response (Text to Speech)">
                        <i class="fas fa-volume-up"></i> Voice Output
                    </button>
                </div>
            `;
        }

        const html = `
            <div class="flex justify-start mb-3">
                <div class="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0">
                    <i class="fas fa-user-tie"></i>
                </div>
                <div class="bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 p-3 rounded-2xl rounded-tl-none max-w-[85%] text-sm shadow border border-gray-100 dark:border-gray-700">
                    <div class="flex items-center justify-between text-[10px] text-gray-400 mb-1 pb-1 border-b border-gray-100 dark:border-gray-700">
                        <span class="font-bold text-blue-600 dark:text-blue-400">👤 मुकेश अजमेरा सलाहकार</span>
                        <span class="text-gray-400 text-[10px]">${timeStr}</span>
                    </div>
                    <div>${formattedText}</div>
                    ${ctaButtonHtml}
                </div>
            </div>
        `;
        $('#chat-messages').append(html);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const html = `
            <div id="typing-indicator" class="flex justify-start mb-3">
                <div class="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0">
                    <i class="fas fa-user-tie"></i>
                </div>
                <div class="bg-white dark:bg-gray-800 p-3 rounded-2xl rounded-tl-none text-xs text-gray-500 shadow border border-gray-100 dark:border-gray-700 flex items-center gap-1.5">
                    <span class="font-semibold text-blue-600 dark:text-blue-400">मुकेश अजमेरा टाइप कर रहे हैं...</span>
                    <span class="flex gap-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-blue-600 animate-bounce"></span>
                        <span class="w-1.5 h-1.5 rounded-full bg-blue-600 animate-bounce [animation-delay:0.2s]"></span>
                        <span class="w-1.5 h-1.5 rounded-full bg-blue-600 animate-bounce [animation-delay:0.4s]"></span>
                    </span>
                </div>
            </div>
        `;
        $('#chat-messages').append(html);
        scrollToBottom();
    }

    function hideTypingIndicator() {
        $('#typing-indicator').remove();
    }

    function scrollToBottom() {
        const container = $('#chat-messages');
        container.scrollTop(container[0].scrollHeight);
    }

    function escapeHtml(text) {
        return $('<div>').text(text).html();
    }

    // Voice Recognition Integration (Speech to Text)
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'hi-IN'; // Default Hindi / Hinglish recognition
        recognition.interimResults = false;

        $('#chat-voice-btn').on('click', function() {
            recognition.start();
            $(this).addClass('text-red-500 animate-pulse');
        });

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            $('#chat-input').val(transcript);
            $('#chat-voice-btn').removeClass('text-red-500 animate-pulse');
        };

        recognition.onerror = function() {
            $('#chat-voice-btn').removeClass('text-red-500 animate-pulse');
        };

        recognition.onend = function() {
            $('#chat-voice-btn').removeClass('text-red-500 animate-pulse');
        };
    } else {
        $('#chat-voice-btn').hide();
    }
});

// Text-to-Speech (Voice Output) Helper for Human-like Advisor Audio
function speakText(btn) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel(); // Stop any active speech
        const rawText = $(btn).attr('data-text') || '';
        if (!rawText) return;

        const utterance = new SpeechSynthesisUtterance(rawText);
        utterance.lang = 'hi-IN';
        utterance.rate = 0.95; // Natural human advisor pace
        utterance.pitch = 1.0;
        
        $(btn).addClass('text-emerald-500 animate-pulse');
        utterance.onend = function() {
            $(btn).removeClass('text-emerald-500 animate-pulse');
        };
        utterance.onerror = function() {
            $(btn).removeClass('text-emerald-500 animate-pulse');
        };

        window.speechSynthesis.speak(utterance);
    }
}

