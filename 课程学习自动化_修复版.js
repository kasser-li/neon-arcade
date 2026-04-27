// ==UserScript==
// @name         课程学习自动化修复版
// @namespace    http://tampermonkey.net/
// @version      4.1
// @description  修复按钮查找逻辑，区分课程列表和播放按钮
// @author       YourName
// @match        *://*/*
// @grant        none
// @license      MIT
// ==/UserScript==

(function() {
    'use strict';

    // ==================== 全局配置 ====================
    const CONFIG = {
        video: {
            playbackRate: 2.0,
            lockSpeed: true,
            lockInterval: 1000,
            scanInterval: 2000,
            autoPlay: true
        },
        
        course: {
            scanInterval: 3000,      // 课程检查间隔（稍长，避免频繁）
            buttonScanInterval: 1000, // 按钮检查间隔（更频繁）
            maxRetries: 5,
            
            // 课程列表选择器（侧边栏/课程列表）
            courseListSelectors: {
                container: ['.course-list', '.lesson-list', '.chapter-list', '.menu-list', '.sidebar'],
                item: ['.item-web', '.item', '.course-item', '.lesson-item', '.chapter-item'],
                currentItem: ['.curr', '.active', '.current', '.playing'],
                completedTag: ['.tag-green', '.completed', '.finished']
            },
            
            // 播放控制按钮选择器（视频区域）
            playButtonSelectors: {
                // 主播放按钮
                primary: [
                    '.btn-start',           // 开始学习
                    '.btn-continue',        // 继续学习
                    '.btn-play',            // 播放按钮
                    '.btn-replay',          // 重新播放
                    '.start-btn',
                    '.continue-btn',
                    '.play-btn'
                ],
                // 视频覆盖层点击
                overlay: [
                    '.video-cover',         // 视频封面
                    '.cover',               // 封面
                    '.player-cover',
                    '.video-overlay'
                ],
                // 图标按钮
                icon: [
                    '.icon-play',           // 播放图标
                    '.icon-start',
                    '.play-icon',
                    '[class*="play"] i',
                    '[class*="start"] i'
                ]
            }
        },
        
        debug: true
    };

    function log(module, ...args) {
        if (CONFIG.debug) {
            console.log(`[${module}]`, ...args);
        }
    }

    // ==================== 工具函数 ====================
    
    function isVisible(el) {
        if (!el) return false;
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' && 
               style.opacity !== '0' &&
               !el.disabled &&
               rect.width > 0 && 
               rect.height > 0;
    }

    function clickElement(el) {
        if (!el || !isVisible(el)) return false;
        
        try {
            // 高亮显示
            el.style.outline = '3px solid red';
            setTimeout(() => el.style.outline = '', 1000);
            
            // 多种点击方式
            el.click();
            el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
            el.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
            el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
            
            log('点击', '✅ 点击成功:', el.className?.substring(0, 50));
            return true;
        } catch (e) {
            log('点击', '❌ 点击失败:', e);
            return false;
        }
    }

    // ==================== 课程列表模块 ====================
    
    const CourseList = {
        // 获取课程列表容器
        getContainer() {
            for (const selector of CONFIG.course.courseListSelectors.container) {
                const el = document.querySelector(selector);
                if (el) return el;
            }
            return document.body;
        },
        
        // 获取所有课程项
        getItems() {
            const container = this.getContainer();
            for (const selector of CONFIG.course.courseListSelectors.item) {
                const items = container.querySelectorAll(selector);
                if (items.length > 0) return Array.from(items);
            }
            return [];
        },
        
        // 获取当前课程
        getCurrent() {
            // 方法1: 通过current类
            for (const selector of CONFIG.course.courseListSelectors.currentItem) {
                const current = document.querySelector(selector);
                if (current) return current;
            }
            
            // 方法2: 通过视频位置
            const video = document.querySelector('video');
            if (video) {
                let parent = video.parentElement;
                while (parent && parent !== document.body) {
                    for (const selector of CONFIG.course.courseListSelectors.item) {
                        if (parent.matches && parent.matches(selector)) {
                            return parent;
                        }
                    }
                    parent = parent.parentElement;
                }
            }
            return null;
        },
        
        // 检查课程是否完成
        isCompleted(item) {
            if (!item) return false;
            
            // 检查完成标签
            for (const selector of CONFIG.course.courseListSelectors.completedTag) {
                const tag = item.querySelector(selector);
                if (tag && isVisible(tag)) {
                    log('课程', '✅ 课程已完成（标签）');
                    return true;
                }
            }
            
            // 检查文本
            const text = item.textContent || '';
            if (text.includes('已完成') || text.includes('已学完') || text.includes('100%')) {
                log('课程', '✅ 课程已完成（文本）');
                return true;
            }
            
            return false;
        },
        
        // 获取课程名称
        getName(item) {
            const nameEl = item.querySelector('.item-name, .course-name, .lesson-title, .title');
            return nameEl ? nameEl.textContent.trim() : '未知课程';
        },
        
        // 查找下一个未完成的课程
        findNext() {
            const items = this.getItems();
            const current = this.getCurrent();
            let foundCurrent = false;
            
            for (const item of items) {
                if (foundCurrent && !this.isCompleted(item)) {
                    return item;
                }
                if (item === current) {
                    foundCurrent = true;
                }
            }
            return null;
        },
        
        // 点击课程项（进入课程）
        async clickItem(item) {
            log('课程', `🎯 点击进入课程: ${this.getName(item)}`);
            
            // 滚动到可视区域
            item.scrollIntoView({ behavior: 'smooth', block: 'center' });
            await new Promise(r => setTimeout(r, 500);
            
            return clickElement(item);
        }
    };

    // ==================== 播放按钮模块（独立）====================
    
    const PlayButton = {
        attempts: new Map(),
        lastClickTime: 0,
        
        // 查找播放按钮（只在视频区域内查找）
        find() {
            // 1. 先找到视频播放器区域
            const videoPlayer = this.findVideoPlayer();
            if (!videoPlayer) {
                log('播放按钮', '⚠️ 未找到视频播放器区域');
                return null;
            }
            
            // 2. 在播放器区域内查找播放按钮
            const searchArea = videoPlayer.parentElement || videoPlayer;
            
            // 方法1: 查找主按钮
            for (const selector of CONFIG.course.playButtonSelectors.primary) {
                const btn = searchArea.querySelector(selector);
                if (btn && isVisible(btn)) {
                    log('播放按钮', '✅ 找到主播放按钮:', selector);
                    return btn;
                }
            }
            
            // 方法2: 查找覆盖层
            for (const selector of CONFIG.course.playButtonSelectors.overlay) {
                const overlay = searchArea.querySelector(selector);
                if (overlay && isVisible(overlay)) {
                    log('播放按钮', '✅ 找到视频覆盖层:', selector);
                    return overlay;
                }
            }
            
            // 方法3: 查找图标按钮
            for (const selector of CONFIG.course.playButtonSelectors.icon) {
                const icon = searchArea.querySelector(selector);
                if (icon && isVisible(icon)) {
                    // 返回图标或其父按钮
                    const parentBtn = icon.closest('button, a, div');
                    if (parentBtn && isVisible(parentBtn)) {
                        log('播放按钮', '✅ 找到图标播放按钮');
                        return parentBtn;
                    }
                    return icon;
                }
            }
            
            // 方法4: 查找包含关键词的按钮
            const buttons = searchArea.querySelectorAll('button, a, div[role="button"]');
            for (const btn of buttons) {
                if (!isVisible(btn)) continue;
                const text = (btn.textContent || '').toLowerCase();
                if (text.includes('开始') || text.includes('继续') || text.includes('播放') || 
                    text.includes('学习') || text.includes('观看')) {
                    log('播放按钮', '✅ 找到文本播放按钮:', text);
                    return btn;
                }
            }
            
            return null;
        },
        
        // 查找视频播放器区域
        findVideoPlayer() {
            // 方法1: 直接找video标签
            const video = document.querySelector('video');
            if (video) return video;
            
            // 方法2: 找播放器容器
            const player = document.querySelector('.video-player, .player, .xgplayer, .video-container');
            if (player) return player;
            
            // 方法3: 找主内容区域
            const main = document.querySelector('.main-content, .content, .video-area');
            if (main) return main;
            
            return null;
        },
        
        // 检查视频是否正在播放
        isVideoPlaying() {
            const video = document.querySelector('video');
            if (!video) return false;
            return !video.paused && video.currentTime > 0 && !video.ended;
        },
        
        // 尝试点击播放按钮
        async tryClick() {
            // 如果视频已在播放，不需要点击
            if (this.isVideoPlaying()) {
                log('播放按钮', '▶️ 视频正在播放');
                return true;
            }
            
            // 防频繁点击
            const now = Date.now();
            if (now - this.lastClickTime < 3000) {
                return false;
            }
            
            const button = this.find();
            if (!button) {
                log('播放按钮', '⚠️ 未找到播放按钮');
                return false;
            }
            
            this.lastClickTime = now;
            log('播放按钮', '🎯 尝试点击播放按钮');
            
            // 滚动到可视区域
            button.scrollIntoView({ behavior: 'smooth', block: 'center' });
            await new Promise(r => setTimeout(r, 500));
            
            return clickElement(button);
        }
    };

    // ==================== 视频倍速模块 ====================
    
    const VideoSpeed = {
        processed: new WeakSet(),
        
        setSpeed(video) {
            if (!video || this.processed.has(video)) return;
            
            try {
                video.playbackRate = CONFIG.video.playbackRate;
                
                if (CONFIG.video.autoPlay && video.paused) {
                    video.play().catch(e => {});
                }
                
                this.processed.add(video);
                log('倍速', `✅ 设置${CONFIG.video.playbackRate}x`);
                
                // 锁定速度
                video.addEventListener('ratechange', () => {
                    if (CONFIG.video.lockSpeed && video.playbackRate !== CONFIG.video.playbackRate) {
                        video.playbackRate = CONFIG.video.playbackRate;
                    }
                });
            } catch (e) {}
        },
        
        scan() {
            document.querySelectorAll('video').forEach(v => this.setSpeed(v));
        },
        
        init() {
            setInterval(() => this.scan(), CONFIG.video.scanInterval);
            setTimeout(() => this.scan(), 1000);
        }
    };

    // ==================== 主控制模块 ====================
    
    const Controller = {
        async checkAndProceed() {
            const currentCourse = CourseList.getCurrent();
            
            // 情况1: 没有当前课程，尝试进入第一个未完成的
            if (!currentCourse) {
                log('控制', '⚠️ 无当前课程，查找第一个未完成的');
                const items = CourseList.getItems();
                for (const item of items) {
                    if (!CourseList.isCompleted(item)) {
                        await CourseList.clickItem(item);
                        return;
                    }
                }
                log('控制', '🎉 所有课程已完成！');
                return;
            }
            
            const courseName = CourseList.getName(currentCourse);
            log('控制', `📚 当前: ${courseName}`);
            
            // 情况2: 当前课程已完成，切换到下一课
            if (CourseList.isCompleted(currentCourse)) {
                log('控制', '✅ 当前课程完成，切换下一课');
                const next = CourseList.findNext();
                if (next) {
                    await CourseList.clickItem(next);
                } else {
                    log('控制', '🎉 全部完成！');
                }
                return;
            }
            
            // 情况3: 课程未完成，检查是否需要点击播放按钮
            log('控制', '⏹️ 课程未完成，检查播放按钮');
            await PlayButton.tryClick();
        },
        
        init() {
            // 启动视频倍速
            VideoSpeed.init();
            
            // 定时检查课程状态
            setInterval(() => this.checkAndProceed(), CONFIG.course.scanInterval);
            setTimeout(() => this.checkAndProceed(), 2000);
            
            // 更频繁地检查播放按钮
            setInterval(() => PlayButton.tryClick(), CONFIG.course.buttonScanInterval);
            
            log('系统', '========================================');
            log('系统', '🎓 课程学习自动化 v4.1 启动');
            log('系统', '========================================');
        }
    };

    // ==================== 初始化 ====================
    
    // 控制台命令
    window.setSpeed = (rate) => {
        CONFIG.video.playbackRate = rate;
        document.querySelectorAll('video').forEach(v => v.playbackRate = rate);
    };
    window.check = () => Controller.checkAndProceed();
    window.findButton = () => PlayButton.find();
    window.findCourse = () => CourseList.getCurrent();
    
    // 快捷键
    document.addEventListener('keydown', (e) => {
        if (e.altKey) {
            if (e.key >= '1' && e.key <= '9') window.setSpeed(parseInt(e.key));
            if (e.key === 'c') window.check();
            if (e.key === 'b') console.log('播放按钮:', window.findButton());
        }
    });
    
    // 启动
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => Controller.init());
    } else {
        Controller.init();
    }

})();