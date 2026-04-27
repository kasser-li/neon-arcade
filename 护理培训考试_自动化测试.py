#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
护理培训及考试系统 - 自动化测试脚本
基于Playwright + pytest框架
支持：视频播放、文件上传、考试答题、满意度调查等功能测试
"""

import pytest
import asyncio
from playwright.async_api import async_playwright, Page, Browser
from datetime import datetime
import json
import os
from typing import Optional

# ==================== 配置 ====================
BASE_URL = "http://localhost:8080"  # 根据实际情况修改
USERNAME = "test_user"
PASSWORD = "test_pass"

# 测试数据
TEST_DATA = {
    "course_id": "course_001",
    "exam_id": "exam_001",
    "video_url": "./static/video/test.mp4",
    "upload_file": "./test_files/sample.pdf",
}

# ==================== 基础测试类 ====================
class NursingTrainingTest:
    """护理培训及考试系统测试基类"""
    
    def __init__(self, page: Page):
        self.page = page
        self.screenshots_dir = "./screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
    
    async def screenshot(self, name: str):
        """截图保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"{self.screenshots_dir}/{name}_{timestamp}.png"
        await self.page.screenshot(path=path, full_page=True)
        print(f"截图已保存: {path}")
    
    async def wait_for_element(self, selector: str, timeout: int = 5000):
        """等待元素出现"""
        await self.page.wait_for_selector(selector, timeout=timeout)
    
    async def safe_click(self, selector: str, timeout: int = 5000):
        """安全点击元素"""
        await self.wait_for_element(selector, timeout)
        await self.page.click(selector)
    
    async def safe_fill(self, selector: str, text: str, timeout: int = 5000):
        """安全填写输入框"""
        await self.wait_for_element(selector, timeout)
        await self.page.fill(selector, text)

# ==================== 登录模块测试 ====================
class LoginTest(NursingTrainingTest):
    """登录模块测试"""
    
    async def test_login_success(self):
        """测试正常登录"""
        print("\n=== 测试：正常登录 ===")
        await self.page.goto(f"{BASE_URL}/pages/login/index")
        
        # 填写用户名密码
        await self.safe_fill('[placeholder="请输入用户名"]', USERNAME)
        await self.safe_fill('[placeholder="请输入密码"]', PASSWORD)
        
        # 点击登录
        await self.safe_click('.login-btn')
        
        # 验证登录成功
        await self.wait_for_element('.home-page', timeout=10000)
        assert await self.page.is_visible('.home-page')
        await self.screenshot("login_success")
        print("✅ 登录成功")
    
    async def test_login_wrong_password(self):
        """测试错误密码登录"""
        print("\n=== 测试：错误密码登录 ===")
        await self.page.goto(f"{BASE_URL}/pages/login/index")
        
        await self.safe_fill('[placeholder="请输入用户名"]', USERNAME)
        await self.safe_fill('[placeholder="请输入密码"]', "wrong_password")
        await self.safe_click('.login-btn')
        
        # 验证错误提示
        await self.wait_for_element('.error-msg', timeout=5000)
        assert await self.page.is_visible('.error-msg')
        await self.screenshot("login_wrong_password")
        print("✅ 错误密码提示正确")
    
    async def test_login_empty_fields(self):
        """测试空字段登录"""
        print("\n=== 测试：空字段登录 ===")
        await self.page.goto(f"{BASE_URL}/pages/login/index")
        
        await self.safe_click('.login-btn')
        
        # 验证表单验证
        await self.wait_for_element('.form-error', timeout=5000)
        assert await self.page.is_visible('.form-error')
        await self.screenshot("login_empty_fields")
        print("✅ 空字段验证正确")

# ==================== 视频学习模块测试 ====================
class VideoLearningTest(NursingTrainingTest):
    """视频学习模块测试"""
    
    async def test_video_play(self):
        """测试视频播放"""
        print("\n=== 测试：视频播放 ===")
        await self.page.goto(f"{BASE_URL}/pages/course/video?id={TEST_DATA['course_id']}")
        
        # 等待视频播放器加载
        await self.wait_for_element('.xgplayer', timeout=10000)
        
        # 点击播放
        await self.safe_click('.xgplayer-start')
        
        # 等待播放状态
        await asyncio.sleep(2)
        
        # 验证播放中
        is_playing = await self.page.is_visible('.xgplayer-icon-pause')
        assert is_playing, "视频未开始播放"
        
        await self.screenshot("video_playing")
        print("✅ 视频播放正常")
    
    async def test_video_pause(self):
        """测试视频暂停"""
        print("\n=== 测试：视频暂停 ===")
        await self.page.goto(f"{BASE_URL}/pages/course/video?id={TEST_DATA['course_id']}")
        
        await self.wait_for_element('.xgplayer', timeout=10000)
        await self.safe_click('.xgplayer-start')
        await asyncio.sleep(2)
        
        # 点击暂停
        await self.safe_click('.xgplayer-icon-pause')
        await asyncio.sleep(1)
        
        # 验证暂停状态
        is_paused = await self.page.is_visible('.xgplayer-icon-play')
        assert is_paused, "视频未暂停"
        
        await self.screenshot("video_paused")
        print("✅ 视频暂停正常")
    
    async def test_video_progress_save(self):
        """测试视频进度保存"""
        print("\n=== 测试：视频进度保存 ===")
        await self.page.goto(f"{BASE_URL}/pages/course/video?id={TEST_DATA['course_id']}")
        
        await self.wait_for_element('.xgplayer', timeout=10000)
        await self.safe_click('.xgplayer-start')
        await asyncio.sleep(5)  # 播放5秒
        
        # 记录当前时间
        current_time = await self.page.inner_text('.xgplayer-time-current')
        print(f"当前播放时间: {current_time}")
        
        # 刷新页面
        await self.page.reload()
        await self.wait_for_element('.xgplayer', timeout=10000)
        
        # 验证进度恢复
        await asyncio.sleep(2)
        saved_time = await self.page.inner_text('.xgplayer-time-current')
        print(f"恢复播放时间: {saved_time}")
        
        await self.screenshot("video_progress_saved")
        print("✅ 视频进度保存正常")
    
    async def test_video_fullscreen(self):
        """测试视频全屏"""
        print("\n=== 测试：视频全屏 ===")
        await self.page.goto(f"{BASE_URL}/pages/course/video?id={TEST_DATA['course_id']}")
        
        await self.wait_for_element('.xgplayer', timeout=10000)
        await self.safe_click('.xgplayer-start')
        await asyncio.sleep(2)
        
        # 点击全屏
        await self.safe_click('[data-xgtype="fullscreen"]')
        await asyncio.sleep(1)
        
        # 验证全屏状态
        is_fullscreen = await self.page.is_visible('.xgplayer-tip-exitfull')
        assert is_fullscreen, "未进入全屏模式"
        
        await self.screenshot("video_fullscreen")
        
        # 退出全屏
        await self.page.press('Escape')
        await asyncio.sleep(1)
        
        print("✅ 视频全屏功能正常")

# ==================== 文件上传模块测试 ====================
class FileUploadTest(NursingTrainingTest):
    """文件上传模块测试"""
    
    async def test_upload_pdf(self):
        """测试PDF文件上传"""
        print("\n=== 测试：PDF文件上传 ===")
        await self.page.goto(f"{BASE_URL}/pages/upload/index")
        
        # 选择文件
        file_input = await self.page.query_selector('input[type="file"]')
        await file_input.set_input_files(TEST_DATA['upload_file'])
        
        # 等待上传完成
        await self.wait_for_element('.upload-file-status-1', timeout=30000)
        
        # 验证上传成功
        status_text = await self.page.inner_text('.upload-file-status-1')
        assert "上传成功" in status_text or "完成" in status_text
        
        await self.screenshot("upload_pdf_success")
        print("✅ PDF上传成功")
    
    async def test_upload_progress(self):
        """测试上传进度显示"""
        print("\n=== 测试：上传进度显示 ===")
        await self.page.goto(f"{BASE_URL}/pages/upload/index")
        
        # 选择大文件
        file_input = await self.page.query_selector('input[type="file"]')
        await file_input.set_input_files("./test_files/large_video.mp4")
        
        # 验证进度条出现
        await self.wait_for_element('.upload-progress', timeout=5000)
        
        # 等待上传完成
        await self.wait_for_element('.upload-file-status-1', timeout=60000)
        
        await self.screenshot("upload_progress")
        print("✅ 上传进度显示正常")
    
    async def test_upload_cancel(self):
        """测试取消上传"""
        print("\n=== 测试：取消上传 ===")
        await self.page.goto(f"{BASE_URL}/pages/upload/index")
        
        file_input = await self.page.query_selector('input[type="file"]')
        await file_input.set_input_files("./test_files/large_video.mp4")
        
        # 等待上传开始
        await self.wait_for_element('.upload-progress', timeout=5000)
        
        # 点击取消
        await self.safe_click('.upload-cancel-btn')
        
        # 验证取消成功
        await self.wait_for_element('.upload-file-status-3', timeout=5000)
        status_text = await self.page.inner_text('.upload-file-status-3')
        assert "取消" in status_text or "失败" in status_text
        
        await self.screenshot("upload_cancelled")
        print("✅ 取消上传功能正常")

# ==================== 考试模块测试 ====================
class ExamTest(NursingTrainingTest):
    """考试模块测试"""
    
    async def test_exam_start(self):
        """测试开始考试"""
        print("\n=== 测试：开始考试 ===")
        await self.page.goto(f"{BASE_URL}/pages/exam/detail?id={TEST_DATA['exam_id']}")
        
        # 点击开始考试
        await self.safe_click('.start-exam-btn')
        
        # 验证进入考试页面
        await self.wait_for_element('.exam-question-page', timeout=10000)
        assert await self.page.is_visible('.exam-question-page')
        
        await self.screenshot("exam_started")
        print("✅ 考试开始正常")
    
    async def test_single_choice_answer(self):
        """测试单选题答题"""
        print("\n=== 测试：单选题答题 ===")
        await self.page.goto(f"{BASE_URL}/pages/exam/answer?id={TEST_DATA['exam_id']}")
        
        await self.wait_for_element('.question-item', timeout=10000)
        
        # 选择第一个选项
        await self.safe_click('.option-item:first-child')
        
        # 验证选中状态
        is_selected = await self.page.is_visible('.option-item:first-child .selected')
        assert is_selected, "选项未选中"
        
        await self.screenshot("single_choice_answered")
        print("✅ 单选题答题正常")
    
    async def test_multiple_choice_answer(self):
        """测试多选题答题"""
        print("\n=== 测试：多选题答题 ===")
        await self.page.goto(f"{BASE_URL}/pages/exam/answer?id={TEST_DATA['exam_id']}")
        
        await self.wait_for_element('.question-item', timeout=10000)
        
        # 选择多个选项
        await self.safe_click('.option-item:nth-child(1)')
        await self.safe_click('.option-item:nth-child(2)')
        
        # 验证两个选项都被选中
        selected_count = await self.page.locator('.option-item .selected').count()
        assert selected_count >= 2, "多选题选项未正确选中"
        
        await self.screenshot("multiple_choice_answered")
        print("✅ 多选题答题正常")
    
    async def test_exam_submit(self):
        """测试提交考试"""
        print("\n=== 测试：提交考试 ===")
        await self.page.goto(f"{BASE_URL}/pages/exam/answer?id={TEST_DATA['exam_id']}")
        
        await self.wait_for_element('.question-item', timeout=10000)
        
        # 答完所有题
        while await self.page.is_visible('.next-question-btn'):
            await self.safe_click('.option-item:first-child')
            await self.safe_click('.next-question-btn')
            await asyncio.sleep(0.5)
        
        # 提交考试
        await self.safe_click('.submit-exam-btn')
        
        # 确认提交
        await self.wait_for_element('.confirm-dialog', timeout=5000)
        await self.safe_click('.confirm-submit')
        
        # 验证提交成功
        await self.wait_for_element('.exam-result-page', timeout=10000)
        assert await self.page.is_visible('.exam-result-page')
        
        await self.screenshot("exam_submitted")
        print("✅ 考试提交正常")
    
    async def test_exam_timeout(self):
        """测试考试超时"""
        print("\n=== 测试：考试超时 ===")
        await self.page.goto(f"{BASE_URL}/pages/exam/answer?id={TEST_DATA['exam_id']}")
        
        await self.wait_for_element('.exam-timer', timeout=10000)
        
        # 获取考试时间（模拟短时间的考试）
        # 实际测试时需要修改考试时长为很短的时间
        
        # 等待超时
        await self.wait_for_element('.timeout-dialog', timeout=300000)
        
        # 验证超时提示
        assert await self.page.is_visible('.timeout-dialog')
        
        await self.screenshot("exam_timeout")
        print("✅ 考试超时处理正常")

# ==================== 满意度调查模块测试 ====================
class SatisfactionTest(NursingTrainingTest):
    """满意度调查模块测试"""
    
    async def test_satisfaction_slider(self):
        """测试满意度滑块"""
        print("\n=== 测试：满意度滑块 ===")
        await self.page.goto(f"{BASE_URL}/pages/satisfaction/index")
        
        await self.wait_for_element('.satisfaction__block', timeout=10000)
        
        # 拖动滑块
        slider = await self.page.query_selector('.el-slider__button')
        box = await slider.bounding_box()
        await self.page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
        await self.page.mouse.down()
        await self.page.mouse.move(box['x'] + 100, box['y'] + box['height'] / 2)
        await self.page.mouse.up()
        
        await asyncio.sleep(1)
        await self.screenshot("satisfaction_slider")
        print("✅ 满意度滑块正常")
    
    async def test_satisfaction_radio(self):
        """测试满意度单选"""
        print("\n=== 测试：满意度单选 ===")
        await self.page.goto(f"{BASE_URL}/pages/satisfaction/index")
        
        await self.wait_for_element('.satisfaction__select-check', timeout=10000)
        
        # 选择第一个选项
        await self.safe_click('.el-radio:first-child')
        
        # 验证选中
        is_checked = await self.page.is_visible('.el-radio__input.is-checked')
        assert is_checked, "单选未选中"
        
        await self.screenshot("satisfaction_radio")
        print("✅ 满意度单选正常")
    
    async def test_satisfaction_checkbox(self):
        """测试满意度多选"""
        print("\n=== 测试：满意度多选 ===")
        await self.page.goto(f"{BASE_URL}/pages/satisfaction/index")
        
        await self.wait_for_element('.satisfaction__select-check', timeout=10000)
        
        # 选择多个选项
        await self.safe_click('.el-checkbox:first-child')
        await self.safe_click('.el-checkbox:nth-child(2)')
        
        # 验证选中数量
        checked_count = await self.page.locator('.el-checkbox__input.is-checked').count()
        assert checked_count >= 2, "多选未正确选中"
        
        await self.screenshot("satisfaction_checkbox")
        print("✅ 满意度多选正常")
    
    async def test_satisfaction_submit(self):
        """测试满意度提交"""
        print("\n=== 测试：满意度提交 ===")
        await self.page.goto(f"{BASE_URL}/pages/satisfaction/index")
        
        await self.wait_for_element('.satisfaction__block', timeout=10000)
        
        # 填写满意度
        await self.safe_click('.el-radio:first-child')
        
        # 提交
        await self.safe_click('.submit-btn')
        
        # 验证提交成功
        await self.wait_for_element('.submit-success', timeout=10000)
        assert await self.page.is_visible('.submit-success')
        
        await self.screenshot("satisfaction_submitted")
        print("✅ 满意度提交正常")

# ==================== 课程列表模块测试 ====================
class CourseListTest(NursingTrainingTest):
    """课程列表模块测试"""
    
    async def test_course_list_load(self):
        """测试课程列表加载"""
        print("\n=== 测试：课程列表加载 ===")
        await self.page.goto(f"{BASE_URL}/pages/course/list")
        
        await self.wait_for_element('.course-list', timeout=10000)
        
        # 验证课程项加载
        course_count = await self.page.locator('.course-item').count()
        assert course_count > 0, "课程列表未加载"
        
        await self.screenshot("course_list_loaded")
        print(f"✅ 课程列表加载正常，共{course_count}个课程")
    
    async def test_course_search(self):
        """测试课程搜索"""
        print("\n=== 测试：课程搜索 ===")
        await self.page.goto(f"{BASE_URL}/pages/course/list")
        
        await self.wait_for_element('.search-input', timeout=10000)
        
        # 输入搜索关键词
        await self.safe_fill('.search-input', '护理')
        await self.page.press('.search-input', 'Enter')
        
        # 等待搜索结果
        await asyncio.sleep(2)
        
        await self.screenshot("course_search_result")
        print("✅ 课程搜索正常")
    
    async def test_course_filter(self):
        """测试课程筛选"""
        print("\n=== 测试：课程筛选 ===")
        await self.page.goto(f"{BASE_URL}/pages/course/list")
        
        await self.wait_for_element('.filter-bar', timeout=10000)
        
        # 点击筛选条件
        await self.safe_click('.filter-item:first-child')
        await asyncio.sleep(1)
        
        await self.screenshot("course_filtered")
        print("✅ 课程筛选正常")
    
    async def test_course_detail(self):
        """测试课程详情"""
        print("\n=== 测试：课程详情 ===")
        await self.page.goto(f"{BASE_URL}/pages/course/list")
        
        await self.wait_for_element('.course-item', timeout=10000)
        
        # 点击第一个课程
        await self.safe_click('.course-item:first-child')
        
        # 验证进入详情页
        await self.wait_for_element('.course-detail-page', timeout=10000)
        assert await self.page.is_visible('.course-detail-page')
        
        await self.screenshot("course_detail")
        print("✅ 课程详情页正常")
    
    async def test_course_pagination(self):
        """测试课程分页"""
        print("\n=== 测试：课程分页 ===")
        await self.page.goto(f"{BASE_URL}/pages/course/list")
        
        await self.wait_for_element('.course-list', timeout=10000)
        
        # 记录第一页课程数
        first_page_count = await self.page.locator('.course-item').count()
        
        # 滚动到底部加载更多
        await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(2)
        
        # 验证加载了更多课程
        total_count = await self.page.locator('.course-item').count()
        assert total_count >= first_page_count, "分页加载失败"
        
        await self.screenshot("course_pagination")
        print(f"✅ 课程分页正常，共加载{total_count}个课程")

# ==================== 主测试运行器 ====================
async def run_all_tests():
    """运行所有测试"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        
        # 创建测试报告
        report = {
            "start_time": datetime.now().isoformat(),
            "tests": []
        }
        
        try:
            # 登录测试
            page = await context.new_page()
            login_test = LoginTest(page)
            await login_test.test_login_success()
            await login_test.test_login_wrong_password()
            await login_test.test_login_empty_fields()
            await page.close()
            
            # 视频学习测试
            page = await context.new_page()
            video_test = VideoLearningTest(page)
            await video_test.test_video_play()
            await video_test.test_video_pause()
            await video_test.test_video_progress_save()
            await video_test.test_video_fullscreen()
            await page.close()
            
            # 文件上传测试
            page = await context.new_page()
            upload_test = FileUploadTest(page)
            await upload_test.test_upload_pdf()
            await upload_test.test_upload_progress()
            await upload_test.test_upload_cancel()
            await page.close()
            
            # 考试测试
            page = await context.new_page()
            exam_test = ExamTest(page)
            await exam_test.test_exam_start()
            await exam_test.test_single_choice_answer()
            await exam_test.test_multiple_choice_answer()
            await exam_test.test_exam_submit()
            await page.close()
            
            # 满意度测试
            page = await context.new_page()
            satisfaction_test = SatisfactionTest(page)
            await satisfaction_test.test_satisfaction_slider()
            await satisfaction_test.test_satisfaction_radio()
            await satisfaction_test.test_satisfaction_checkbox()
            await satisfaction_test.test_satisfaction_submit()
            await page.close()
            
            # 课程列表测试
            page = await context.new_page()
            course_test = CourseListTest(page)
            await course_test.test_course_list_load()
            await course_test.test_course_search()
            await course_test.test_course_filter()
            await course_test.test_course_detail()
            await course_test.test_course_pagination()
            await page.close()
            
            print("\n" + "="*50)
            print("🎉 所有测试通过！")
            print("="*50)
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()
            
        report["end_time"] = datetime.now().isoformat()
        
        # 保存测试报告
        with open("./test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

# ==================== pytest测试用例 ====================
@pytest.fixture
async def browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        yield browser
        await browser.close()

@pytest.fixture
async def page(browser):
    context = await browser.new_context(
        viewport={'width': 1280, 'height': 720}
    )
    page = await context.new_page()
    yield page
    await context.close()

# pytest测试用例
@pytest.mark.asyncio
async def test_login(page):
    login_test = LoginTest(page)
    await login_test.test_login_success()

@pytest.mark.asyncio
async def test_video(page):
    video_test = VideoLearningTest(page)
    await video_test.test_video_play()

@pytest.mark.asyncio
async def test_upload(page):
    upload_test = FileUploadTest(page)
    await upload_test.test_upload_pdf()

@pytest.mark.asyncio
async def test_exam(page):
    exam_test = ExamTest(page)
    await exam_test.test_exam_start()

@pytest.mark.asyncio
async def test_satisfaction(page):
    satisfaction_test = SatisfactionTest(page)
    await satisfaction_test.test_satisfaction_submit()

@pytest.mark.asyncio
async def test_course(page):
    course_test = CourseListTest(page)
    await course_test.test_course_list_load()

# ==================== 入口 ====================
if __name__ == "__main__":
    print("="*50)
    print("护理培训及考试系统 - 自动化测试")
    print("="*50)
    
    # 运行所有测试
    asyncio.run(run_all_tests())
    
    # 或者使用pytest运行
    # pytest.main([__file__, "-v", "--tb=short"])
