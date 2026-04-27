// ==UserScript==
// @name         课程学习自动化优化版
// @namespace    http://tampermonkey.net/
// @version      4.0
// @description  优化自动点击逻辑，增强元素检测，支持更多页面结构
// @author       YourName
// @match        *://*/*
// @grant        none
// @license      MIT
// ==/UserScript==

(function() {
    'use strict';

    // ==================== 全局配置 ====================
    const CONFIG = {
        // 视频倍速配置
        video: {
            playbackRate: 2.0,
            lockSpeed: true,
            lockInterval: 1000,
            scanInterval: 2000,
            autoPlay: true
        },
        
        // 课程自动下一课配置
        course: {
            scanInterval: 2000,
            checkDelay: 1500,
            retryInterval: 2000,
            maxRetries: 10,
            
            // 选择器配置
            selectors: {
                courseItem: ['.item-web', '.item', '[class*="course-item"]', '[class*="lesson-item"]', '.chapter-item'],
                currentClass: ['curr', 'active', 'current', 'playing', 'selected'],
                courseName: ['.item-name', '.course-name', '.lesson-title', '.chapter-name', 'h3', 'h4', '.title'],
                completedTag: ['.tag-green', '.completed', '.finished', '.done', '[class*="complete"]'],
                startButton: ['.btn-start', '.btn-play', '.start-btn', '.play-btn', '.btn-primary', '.btn-blue', 
                             '[class*="start"]', '[class*="play"]', '[class*="begin"]', '.cover', '.video-cover']
            },
            
            completedKeywords: ['已完成', '已学完', '已看完', '100%', '完成', '学完'],
            buttonKeywords: ['开始', '播放', '学习', '进入', '继续', '观看', 'Start', 'Play', 'Continue']
        },
        
        debug: true
    };

    function log(module, ...args) {
        if (CONFIG.debug) {
            console.log(`[${module}]`, ...args);
        }
    }

    // ==================== 增强版工具函数 ====================
    
    function isElementReallyVisible(el) {
        if (!el || !(el instanceof Element)) return false;
        
        try {
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            
            if (style.display === 'none' || style.visibility === 'hidden' || 
                style.opacity === '0' || el.disabled || rect.width === 0 || rect.height === 0) {
                return false;
            }
            
            return { visible: true, rect: rect };
        } catch (e) {
            return false;
        }
    }

    function enhancedSafeClick(element) {
        if (!element) {
            log('点击', '❌ 元素为空');
            return false;
        }

        const visibility = isElementReallyVisible(element);
        if (!visibility || !visibility.visible) {
            log('点击', '❌ 元素不可见，尝试滚动');
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            return new Promise(resolve => {
                setTimeout(() => {
                    resolve(doClick(element));
                }, 800);
            });
        }
        
        return doClick(element);
    }

    function doClick(element) {
        try {
            // 高亮显示要点击的元素（调试用）
            const originalOutline = element.style.outline;
            element.style.outline = '3px solid red';
            setTimeout(() => { element.style.outline = originalOutline; }, 1000);
            
            // 多种点击方式
            element.click();
            
            ['mousedown', 'mouseup', 'click'].forEach(eventType => {
                element.dispatchEvent(new MouseEvent(eventType, { bubbles: true, cancelable: true, view: window }));
            });
            
            // 移动端触摸事件
            element.dispatchEvent(new TouchEvent('touchstart', { bubbles: true, cancelable: true }));
            element.dispatchEvent(new TouchEvent('touchend', { bubbles: true, cancelable: true }));
            
            log('点击', '✅ 点击成功:', element.tagName, element.className?.substring(0, 50));
            return true;
        } catch (error) {
            log('点击', '❌ 点击失败:', error);
            return false;
        }
    }

    // ==================== 增强版课程工具 ====================
    
    const CourseUtils = {
        // 获取所有课程项
        getCourseItems() {
            for (const selector of CONFIG.course.selectors.courseItem) {
                const items = document.querySelectorAll(selector);
                if (items.length > 0) {
                    log('课程工具', `使用选择器 ${selector} 找到 ${items.length} 个课程项`);
                    return Array.from(items);
                }
            }
            return [];
        },

        // 获取当前课程
        getCurrentCourse() {
            // 方法1: 通过currentClass查找
            for (const className of CONFIG.course.selectors.currentClass) {
                const current = document.querySelector(`.${className}`);
                if (current) {
                    log('课程工具', `通过 .${className} 找到当前课程`);
                    return current;
                }
            }
            
            // 方法2: 查找包含视频播放器的课程项
            const videos = document.querySelectorAll('video');
            for (const video of videos) {
                let parent = video.parentElement;
                while (parent && parent !== document.body) {
                    if (parent.classList.contains('item') || parent.classList.contains('item-web')) {
                        log('课程工具', '通过视频播放器找到当前课程');
                        return parent;
                    }
                    parent = parent.parentElement;
                }
            }
            
            return null;
        },

        // 检查课程是否完成
        isCourseCompleted(courseElement) {
            if (!courseElement) return false;
            
            // 方法1: 检查完成标签
            for (const selector of CONFIG.course.selectors.completedTag) {
                const tag = courseElement.querySelector(selector);
                if (tag && isElementReallyVisible(tag)) {
                    log('课程工具', '✅ 检测到完成标签:', selector);
                    return true;
                }
            }
            
            // 方法2: 检查文本内容
            const text = courseElement.textContent || '';
            for (const keyword of CONFIG.course.completedKeywords) {
                if (text.includes(keyword)) {
                    log('课程工具', '✅ 检测到完成关键词:', keyword);
                    return true;
                }
            }
            
            return false;
        },

        // 查找课程名称
        getCourseName(courseElement) {
            for (const selector of CONFIG.course.selectors.courseName) {
                const nameEl = courseElement.querySelector(selector);
                if (nameEl) {
                    return nameEl.textContent.trim();
                }
            }
            return courseElement.textContent?.trim()?.substring(0, 30) || '未知课程';
        },

        // 查找开始按钮（增强版）
        findStartButton(courseElement) {
            log('课程工具', '🔍 开始查找开始按钮...');
            
            // 方法1: 使用预定义选择器
            for (const selector of CONFIG.course.selectors.startButton) {
                const buttons = courseElement.querySelectorAll(selector);
                for (const btn of buttons) {
                    if (isElementReallyVisible(btn)) {
                        log('课程工具', '✅ 找到开始按钮(选择器):', selector);
                        return btn;
                    }
                }
            }
            
            // 方法2: 查找包含关键词的按钮
            const allElements = courseElement.querySelectorAll('button, a, div, span, i');
            for (const el of allElements) {
                if (!isElementReallyVisible(el)) continue;
                
                const text = (el.textContent || '').toLowerCase();
                const className = (el.className || '').toLowerCase();
                
                for (const keyword of CONFIG.course.buttonKeywords) {
                    if (text.includes(keyword.toLowerCase()) || className.includes(keyword.toLowerCase())) {
                        log('课程工具', '✅ 找到开始按钮(关键词):', keyword);
                        return el;
                    }
                }
            }
            
            // 方法3: 查找图标按钮（播放图标）
            const icons = courseElement.querySelectorAll('[class*="icon"], [class*="Icon"], i, svg');
            for (const icon of icons) {
                if (!isElementReallyVisible(icon)) continue;
                const className = (icon.className || '').toLowerCase();
                if (className.includes('play') || className.includes('start') || className.includes('begin')) {
                    // 返回图标或其父元素
                    const parent = icon.closest('button, a, div') || icon;
                    if (isElementReallyVisible(parent)) {
                        log('课程工具', '✅ 找到图标按钮');
                        return parent;
                    }
                }
            }
            
            // 方法4: 如果课程未完成，尝试点击课程项本身
            if (!this.isCourseCompleted(courseElement)) {
                log('课程工具', '⚠️ 未找到明确按钮，尝试点击课程项本身');
                return courseElement;
            }
            
            return null;
        },

        // 查找下一个未完成的课程
        findNextUncompletedCourse(currentCourse) {
            const courses = this.getCourseItems();
            let foundCurrent = false;
            
            for (const course of courses) {
                if (foundCurrent) {
                    if (!this.isCourseCompleted(course)) {
                        return course;
                    }
                }
                if (course === currentCourse || course.contains(currentCourse) || currentCourse.contains(course)) {
                    foundCurrent = true;
                }
            }
            return null;
        }
    };

    // ==================== 视频模块 ====================
    
    const VideoModule = {
        processedVideos: new WeakSet(),
        
        setVideoSpeed(video) {
            if (!video || this.processedVideos.has(video)) return;
            
            try {
                video.playbackRate = CONFIG.video.playbackRate;
                
                // 自动播放
                if (CONFIG.video.autoPlay && video.paused) {
                    video.play().catch(e => log('视频', '自动播放被阻止:', e));
                }
                
                this.processedVideos.add(video);
                log('视频', `✅ 设置视频速度: ${CONFIG.video.playbackRate}x`);
                
                // 添加事件监听
                video.addEventListener('ratechange', () => {
                    if (CONFIG.video.lockSpeed && video.playbackRate !== CONFIG.video.playbackRate) {
                        video.playbackRate = CONFIG.video.playbackRate;
                    }
                });
                
            } catch (e) {
                log('视频', '❌ 设置速度失败:', e);
            }
        },
        
        scanVideos() {
            const videos = document.querySelectorAll('video');
            videos.forEach(v => this.setVideoSpeed(v));
        },
        
        init() {
            setInterval(() => this.scanVideos(), CONFIG.video.scanInterval);
            setTimeout(() => this.scanVideos(), 1000);
            
            // 监听新视频
            new MutationObserver(() => {
                setTimeout(() => this.scanVideos(), 500);
            }).observe(document.body, { childList: true, subtree: true });
        }
    };

    // ==================== 课程模块（核心优化）====================
    
    const CourseModule = {
        isProcessing: false,
        lastClickTime: 0,
        clickAttempts: new Map(),
        
        async processCurrentCourse() {
            if (this.isProcessing) {
                log('课程', '⏳ 正在处理中，跳过');
                return;
            }
            
            this.isProcessing = true;
            
            try {
                const currentCourse = CourseUtils.getCurrentCourse();
                
                if (!currentCourse) {
                    log('课程', '⚠️ 未找到当前课程，尝试查找第一个未完成的课程');
                    const courses = CourseUtils.getCourseItems();
                    for (const course of courses) {
                        if (!CourseUtils.isCourseCompleted(course)) {
                            await this.startCourse(course);
                            return;
                        }
                    }
                    return;
                }
                
                const courseName = CourseUtils.getCourseName(currentCourse);
                log('课程', `📚 当前课程: ${courseName}`);
                
                // 检查是否已完成
                if (CourseUtils.isCourseCompleted(currentCourse)) {
                    log('课程', '✅ 当前课程已完成，查找下一课');
                    await this.goToNextCourse(currentCourse);
                    return;
                }
                
                // 检查是否有视频正在播放
                const videos = document.querySelectorAll('video');
                const playingVideo = Array.from(videos).find(v => !v.paused && v.currentTime > 0);
                
                if (playingVideo) {
                    log('课程', '▶️ 视频正在播放，无需操作');
                    return;
                }
                
                // 需要点击开始按钮
                log('课程', '⏹️ 视频未播放，需要点击开始');
                await this.startCourse(currentCourse);
                
            } finally {
                setTimeout(() => { this.isProcessing = false; }, 1000);
            }
        },
        
        async startCourse(courseElement) {
            const courseName = CourseUtils.getCourseName(courseElement);
            const now = Date.now();
            
            // 防止频繁点击
            if (now - this.lastClickTime < 3000) {
                log('课程', '⏱️ 点击太频繁，等待...');
                return;
            }
            
            // 记录尝试次数
            const attempts = this.clickAttempts.get(courseElement) || 0;
            if (attempts >= CONFIG.course.maxRetries) {
                log('课程', '❌ 已达到最大重试次数，跳过');
                this.clickAttempts.delete(courseElement);
                return;
            }
            
            this.clickAttempts.set(courseElement, attempts + 1);
            
            log('课程', `🎯 尝试点击课程: ${courseName} (第${attempts + 1}次)`);
            
            const button = CourseUtils.findStartButton(courseElement);
            
            if (button) {
                this.lastClickTime = now;
                const success = await enhancedSafeClick(button);
                
                if (success) {
                    log('课程', '✅ 点击成功，等待页面响应...');
                    // 等待后重置尝试次数
                    setTimeout(() => {
                        this.clickAttempts.delete(courseElement);
                    }, 10000);
                } else {
                    log('课程', '❌ 点击失败，将在下次重试');
                }
            } else {
                log('课程', '⚠️ 未找到可点击的按钮');
            }
        },
        
        async goToNextCourse(currentCourse) {
            const nextCourse = CourseUtils.findNextUncompletedCourse(currentCourse);
            
            if (nextCourse) {
                const nextName = CourseUtils.getCourseName(nextCourse);
                log('课程', `➡️ 准备切换到: ${nextName}`);
                await this.startCourse(nextCourse);
            } else {
                log('课程', '🎉 所有课程已完成！');
            }
        },
        
        init() {
            log('课程', '🚀 课程模块初始化');
            
            // 定时检查
            setInterval(() => this.processCurrentCourse(), CONFIG.course.scanInterval);
            
            // 立即执行一次
            setTimeout(() => this.processCurrentCourse(), 2000);
            
            // 监听页面变化
            new MutationObserver(() => {
                setTimeout(() => this.processCurrentCourse(), 1000);
            }).observe(document.body, { childList: true, subtree: true, attributes: true });
        }
    };

    // ==================== 初始化 ====================
    
    function init() {
        log('系统', '========================================');
        log('系统', '🎓 课程学习自动化脚本 v4.0 启动');
        log('系统', '========================================');
        
        VideoModule.init();
        CourseModule.init();
        
        // 控制台命令
        window.setSpeed = (rate) => {
            CONFIG.video.playbackRate = rate;
            document.querySelectorAll('video').forEach(v => v.playbackRate = rate);
            log('系统', `速度已设置为 ${rate}x`);
        };
        
        window.checkNow = () => CourseModule.processCurrentCourse();
        
        window.showStatus = () => {
            const current = CourseUtils.getCurrentCourse();
            const courses = CourseUtils.getCourseItems();
            log('状态', `总课程: ${courses.length}, 当前: ${current ? CourseUtils.getCourseName(current) : '无'}`);
        };
        
        // 快捷键
        document.addEventListener('keydown', (e) => {
            if (e.altKey) {
                if (e.key >= '1' && e.key <= '9') {
                    window.setSpeed(parseInt(e.key));
                } else if (e.key === 'c') {
                    window.checkNow();
                } else if (e.key === 's') {
                    window.showStatus();
                }
            }
        });
        
        log('系统', '快捷键: Alt+1-9调速度 | Alt+C立即检查 | Alt+S显示状态');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();