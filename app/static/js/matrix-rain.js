/**
 * Matrix Rain Animation - Code Rain Effect
 * For SaaS Shop Hero Background
 */

class MatrixRain {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        
        // Default options
        this.options = {
            fontSize: options.fontSize || 16,
            fontFamily: options.fontFamily || 'monospace',
            color: options.color || '#0fa',
            backgroundColor: options.backgroundColor || 'rgba(0, 0, 0, 0.05)',
            speed: options.speed || 1.5,
            density: options.density || 0.98,
            symbols: options.symbols || 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$+-*/=%"\'#&_(),.;:?!\\|{}<>[]^~'
        };
        
        // Set canvas to full window size
        this.resize();
        window.addEventListener('resize', () => this.resize());
        
        this.drops = [];
        this.init();
        
        // Start animation
        this.animate();
    }
    
    resize() {
        const container = this.canvas.parentElement;
        this.canvas.width = container.offsetWidth;
        this.canvas.height = container.offsetHeight;
        
        // Reinitialize drops
        this.init();
    }
    
    init() {
        // Calculate columns
        const columns = Math.floor(this.canvas.width / this.options.fontSize);
        
        // Initialize drops
        this.drops = [];
        for (let i = 0; i < columns; i++) {
            // Random starting position
            this.drops.push({
                x: i * this.options.fontSize,
                y: Math.random() * -100,
                speed: Math.random() * 2 + this.options.speed,
                length: Math.floor(Math.random() * 20) + 5
            });
        }
    }
    
    getRandomSymbol() {
        return this.options.symbols.charAt(Math.floor(Math.random() * this.options.symbols.length));
    }
    
    draw() {
        // Semi-transparent black background to create trail effect
        this.ctx.fillStyle = this.options.backgroundColor;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.font = `${this.options.fontSize}px ${this.options.fontFamily}`;
        this.ctx.fillStyle = this.options.color;
        
        // Draw each drop
        for (let i = 0; i < this.drops.length; i++) {
            const drop = this.drops[i];
            
            // Loop through the drop's length
            for (let j = 0; j < drop.length; j++) {
                const char = this.getRandomSymbol();
                const y = drop.y - (j * this.options.fontSize);
                
                // Make the first character brighter
                if (j === 0) {
                    this.ctx.fillStyle = '#fff';
                } else {
                    // Fade out older characters
                    const alpha = 1 - (j / drop.length);
                    this.ctx.fillStyle = `rgba(15, 255, 170, ${alpha})`;
                }
                
                // Draw character
                if (y > 0 && y < this.canvas.height) {
                    this.ctx.fillText(char, drop.x, y);
                }
            }
            
            // Update position
            drop.y += drop.speed;
            
            // Reset when it goes off screen
            if (drop.y - (drop.length * this.options.fontSize) > this.canvas.height) {
                drop.y = Math.random() * -100; // Random start position
                drop.speed = Math.random() * 2 + this.options.speed;
                drop.length = Math.floor(Math.random() * 20) + 5;
            }
        }
    }
    
    animate() {
        this.draw();
        requestAnimationFrame(() => this.animate());
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Matrix Rain animation for hero section
    const heroMatrixRain = new MatrixRain('matrix-bg', {
        fontSize: 14,
        color: 'rgba(0, 123, 255, 0.7)', // Bootstrap primary color with opacity
        backgroundColor: 'rgba(0, 0, 0, 0.03)',
        speed: 1,
        density: 0.98
    });
    
    // Initialize Matrix Rain animation for features section
    const featuresMatrixRain = new MatrixRain('features-matrix-bg', {
        fontSize: 16,
        color: 'rgba(0, 225, 255, 0.6)', // Cyan color with opacity
        backgroundColor: 'rgba(0, 0, 0, 0.03)',
        speed: 1.2,
        density: 0.95,
        symbols: '01010101'  // Use only binary digits for this section
    });
});
