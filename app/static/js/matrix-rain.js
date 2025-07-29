/**
 * Matrix Rain Animation
 * Creates a falling code effect similar to The Matrix
 */
class MatrixRain {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.warn(`Canvas with id "${canvasId}" not found`);
            return;
        }

        this.ctx = this.canvas.getContext('2d');
        
        // Configuration options
        this.options = {
            fontSize: options.fontSize || 16,
            color: options.color || 'rgba(0, 255, 65, 0.8)',
            backgroundColor: options.backgroundColor || 'rgba(0, 0, 0, 0.05)',
            speed: options.speed || 1,
            density: options.density || 0.95,
            characters: options.characters || 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        };

        // Initialize canvas
        this.init();
        
        // Start animation
        this.animate();

        // Handle window resize
        window.addEventListener('resize', () => this.handleResize());
    }

    init() {
        this.handleResize();
        
        // Initialize drops array
        this.drops = [];
        for (let x = 0; x < this.columns; x++) {
            this.drops[x] = 1;
        }
    }

    handleResize() {
        // Set canvas size to match its parent
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        
        // Calculate columns based on font size
        this.columns = Math.floor(this.canvas.width / this.options.fontSize);
        
        // Reset drops if canvas was resized
        if (this.drops && this.drops.length !== this.columns) {
            this.drops = [];
            for (let x = 0; x < this.columns; x++) {
                this.drops[x] = 1;
            }
        }
    }

    draw() {
        // Set font
        this.ctx.font = `${this.options.fontSize}px monospace`;
        
        // Semi-transparent background for fade effect
        this.ctx.fillStyle = this.options.backgroundColor;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Set text color
        this.ctx.fillStyle = this.options.color;
        
        // Draw the drops
        for (let i = 0; i < this.drops.length; i++) {
            // Pick a random character
            const char = this.options.characters.charAt(
                Math.floor(Math.random() * this.options.characters.length)
            );
            
            // Draw the character
            this.ctx.fillText(
                char,
                i * this.options.fontSize,
                this.drops[i] * this.options.fontSize
            );
            
            // Move the drop down
            if (this.drops[i] * this.options.fontSize > this.canvas.height && Math.random() > this.options.density) {
                this.drops[i] = 0;
            }
            this.drops[i] += this.options.speed;
        }
    }

    animate() {
        this.draw();
        this.animationId = requestAnimationFrame(() => this.animate());
    }

    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    }

    start() {
        this.animate();
    }

    updateOptions(newOptions) {
        this.options = { ...this.options, ...newOptions };
    }
}

/**
 * Digital Rain Effect - Alternative implementation
 */
class DigitalRain {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.warn(`Canvas with id "${canvasId}" not found`);
            return;
        }

        this.ctx = this.canvas.getContext('2d');
        
        this.options = {
            fontSize: options.fontSize || 14,
            color: options.color || '#0F3',
            backgroundColor: options.backgroundColor || 'rgba(0, 0, 0, 0.1)',
            speed: options.speed || 50,
            density: options.density || 0.98,
            ...options
        };

        this.init();
        this.animate();
        
        window.addEventListener('resize', () => this.handleResize());
    }

    init() {
        this.handleResize();
        this.drops = Array(this.columns).fill(1);
    }

    handleResize() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        this.columns = Math.floor(this.canvas.width / this.options.fontSize);
        this.drops = Array(this.columns).fill(1);
    }

    draw() {
        this.ctx.fillStyle = this.options.backgroundColor;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = this.options.color;
        this.ctx.font = `${this.options.fontSize}px monospace`;

        for (let i = 0; i < this.drops.length; i++) {
            const text = String.fromCharCode(Math.random() * 128);
            this.ctx.fillText(text, i * this.options.fontSize, this.drops[i] * this.options.fontSize);

            if (this.drops[i] * this.options.fontSize > this.canvas.height && Math.random() > this.options.density) {
                this.drops[i] = 0;
            }
            this.drops[i]++;
        }
    }

    animate() {
        this.draw();
        setTimeout(() => {
            this.animationId = requestAnimationFrame(() => this.animate());
        }, this.options.speed);
    }

    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    }
}

/**
 * Particle System for additional effects
 */
class ParticleSystem {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.options = {
            particleCount: options.particleCount || 50,
            color: options.color || 'rgba(100, 255, 218, 0.6)',
            size: options.size || 2,
            speed: options.speed || 0.5,
            ...options
        };

        this.init();
        this.animate();
        
        window.addEventListener('resize', () => this.handleResize());
    }

    init() {
        this.handleResize();
        this.createParticles();
    }

    handleResize() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
    }

    createParticles() {
        this.particles = [];
        for (let i = 0; i < this.options.particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * this.options.speed,
                vy: (Math.random() - 0.5) * this.options.speed,
                size: Math.random() * this.options.size + 1
            });
        }
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.particles.forEach(particle => {
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fillStyle = this.options.color;
            this.ctx.fill();
            
            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            // Wrap around edges
            if (particle.x < 0) particle.x = this.canvas.width;
            if (particle.x > this.canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = this.canvas.height;
            if (particle.y > this.canvas.height) particle.y = 0;
        });
    }

    animate() {
        this.draw();
        this.animationId = requestAnimationFrame(() => this.animate());
    }

    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MatrixRain, DigitalRain, ParticleSystem };
}
