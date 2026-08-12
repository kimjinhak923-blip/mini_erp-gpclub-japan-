<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>사내 통합 관리 시스템</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --primary-hover: #1d4ed8;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-color: #1e293b;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --success-color: #10b981;
            --danger-color: #ef4444;
            --warning-color: #f59e0b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* 로그인 화면 */
        #login-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: #0f172a;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }

        .login-card {
            background: var(--card-bg);
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 400px;
        }

        .login-card h2 {
            margin-bottom: 1.5rem;
            text-align: center;
            color: var(--primary-color);
        }

        .form-group {
            margin-bottom: 1.2rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.4rem;
            font-size: 0.9rem;
            font-weight: 600;
        }

        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-size: 0.95rem;
        }

        .btn {
            display: inline-block;
            width: 100%;
            padding: 0.75rem;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .btn:hover {
            background-color: var(--primary-hover);
        }

        .btn-secondary {
            background-color: var(--text-muted);
        }
        .btn-secondary:hover {
            background-color: #475569;
        }

        .btn-inline {
            width: auto;
            padding: 0.5rem 1rem;
        }

        /* 메인 레이아웃 */
        #app-container {
            display: none;
            width: 100%;
            height: 100%;
            flex-direction: row;
        }

        /* 사이드바 */
        sidebar {
            width: 260px;
            background-color: #1e293b;
            color: white;
            display: flex;
            flex-direction: column;
        }

        .sidebar-header {
            padding: 1.5rem;
            font-size: 1.25rem;
            font-weight: bold;
            border-bottom: 1px solid #334155;
            color: #60a5fa;
        }

        .nav-menu {
            list-style: none;
            padding: 1rem 0;
            flex-grow: 1;
        }

        .nav-item {
            padding: 0.85rem 1.5rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            font-size: 0.95rem;
            color: #cbd5e1;
            transition: background 0.2s;
        }

        .nav-item:hover, .nav-item.active {
            background-color: #334155;
            color: white;
            font-weight: 600;
        }

        .user-info {
            padding: 1rem 1.5rem;
            border-top: 1px solid #334155;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
        }

        /* 메인 콘텐츠 영역 */
        main {
            flex-grow: 1;
            overflow-y: auto;
            padding: 2rem;
            background-color: var(--bg-color);
        }

        .content-section {
            display: none;
        }

        .content-section.active {
            display: block;
        }

        /* 출퇴근 위젯 카드가 놓일 첫 화면 상단 */
        .attendance-hero-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: white;
            padding: 1.75rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .time-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            padding-bottom: 1rem;
            margin-bottom: 1.2rem;
        }

        .server-time-title {
            font-size: 0.9rem;
            color: #94a3b8;
        }

        .server-time-clock {
            font-size: 1.5rem;
            font-weight: 700;
            color: #38bdf8;
            letter-spacing: 1px;
        }

        .commute-action-area {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .commute-status-info {
            display: flex;
            gap: 1.5rem;
        }

        .status-box span {
            display: block;
            font-size: 0.8rem;
            color: #94a3b8;
        }

        .status-box strong {
            font-size: 1.1rem;
            color: #f8fafc;
        }

        .btn-group-commute {
            display: flex;
            gap: 0.75rem;
        }

        .btn-commute {
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: transform 0.1s;
        }
        .btn-commute:active {
            transform: scale(0.97);
        }

        .btn-in {
            background-color: var(--success-color);
            color: white;
        }

        .btn-out {
            background-color: var(--danger-color);
            color: white;
        }

        /* 테이블 및 일반 카드 스타일 */
        .card {
            background: var(--card-bg);
            border-radius: 10px;
            padding: 1.5rem;
            border: 1px solid var(--border-color);
            margin-bottom: 1.5rem;
        }

        .card-title {
            font-size: 1.1rem;
            font-weight: bold;
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            font-size: 0.9rem;
        }

        th, td {
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        th {
            background-color: #f1f5f9;
            font-weight: 600;
            color: var(--text-muted);
        }

        .badge {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge-success { background: #d1fae5; color: #065f46; }
        .badge-warning { background: #fef3c7; color: #92400e; }
        .badge-danger  { background: #fee2e2; color: #991b1b; }

        .rules-note {
            font-size: 0.85rem;
            color: #94a3b8;
            margin-top: 0.5rem;
            line-height: 1.4;
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }

        @media (max-width: 768px) {
            .grid-2 { grid-template-columns: 1fr; }
            #app-container { flex-direction: column; }
            sidebar { width: 100%; }
        }
    </style>
</head>
<body>

    <!-- 1. 로그인 화면 -->
    <div id="login-screen">
        <div class="login-card">
            <h2>사내 관리 시스템</h2>
            <form id="login-form" onsubmit="handleLogin(event)">
                <div class="form-group">
                    <label for="login-id">아이디</label>
                    <input type="text" id="login-id" required placeholder="아이디를 입력하세요">
                </div>
                <div class="form-group">
                    <label for="login-pw">비밀번호</label>
                    <input type="password" id="login-pw" required placeholder="비밀번호를 입력하세요">
                </div>
                <button type="submit" class="btn">로그인</button>
            </form>
        </div>
    </div>

    <!-- 2. 메인 애플리케이션 화면 -->
    <div id="app-container">
        <!-- 사이드바 -->
        <sidebar>
            <div class="sidebar-header">WORK MANAGER</div>
            <ul class="nav-menu">
                <li class="nav-item active" onclick="switchTab('dashboard')">대시보드</li>
                <li class="nav-item" onclick="switchTab('attendance')">출퇴근 관리</li>
                <li class="nav-item" onclick="switchTab('employees')">직원 계정 생성/관리</li>
                <li class="nav-item" onclick="switchTab('schedule')">휴가 및 스케줄 관리</li>
                <li class="nav-item" onclick="switchTab('permissions')">시스템 관리 (사용자 권한)</li>
            </ul>
            <div class="user-info">
                <span id="current-user-display">관리자 (admin)</span>
                <button class="btn btn-secondary btn-inline" onclick="handleLogout()" style="font-size:0.75rem; padding:0.3rem 0.6rem;">로그아웃</button>
            </div>
        </sidebar>

        <!-- 메인 콘텐츠 영역 -->
        <main>

            <!-- 로그인 후 첫 화면 최상단 공통 히어로 위젯 (도쿄 기준 서버시간 & 출퇴근) -->
            <div class="attendance-hero-card">
                <div class="time-header">
                    <div>
                        <div class="server-time-title">도쿄 기준 서버 시간 (Asia/Tokyo)</div>
                        <div class="server-time-clock" id="tokyo-clock">2026. 08. 12. 00:00:00 JST</div>
                    </div>
                    <div>
                        <span class="badge badge-success" id="today-date-badge">오늘</span>
                    </div>
                </div>
                <div class="commute-action-area">
                    <div class="commute-status-info">
                        <div class="status-box">
                            <span>출근 기록 시각</span>
                            <strong id="display-clock-in">--:--:--</strong>
                        </div>
                        <div class="status-box">
                            <span>퇴근 기록 시각</span>
                            <strong id="display-clock-out">--:--:--</strong>
                        </div>
                        <div class="status-box">
                            <span>인정 실근무시간</span>
                            <strong id="display-work-hours" style="color: #60a5fa;">0시간 0분</strong>
                        </div>
                    </div>
                    <div class="btn-group-commute">
                        <button class="btn-commute btn-in" onclick="processClockIn()">출근하기</button>
                        <button class="btn-commute btn-out" onclick="processClockOut()">퇴근하기</button>
                    </div>
                </div>
                <div class="rules-note">
                    ※ 근무시간 산정 기준: 출근 시각에 상관없이 근무시간은 <strong>09:00부터 계산</strong>됩니다. (정시퇴근 18:00 / 점심시간 12:00~13:00 차감)
                </div>
            </div>

            <!-- 탭 1: 대시보드 -->
            <section id="tab-dashboard" class="content-section active">
                <div class="grid-2">
                    <div class="card">
                        <div class="card-title">오늘의 근무 상태 현황</div>
                        <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 1rem;">현재 접속 중인 계정의 오늘 출퇴근 기록 현황입니다.</p>
                        <table>
                            <tr>
                                <th>구분</th>
                                <th>시간 / 내용</th>
                            </tr>
                            <tr>
                                <td>기준 시작 시간</td>
                                <td>09:00 (고정 산정)</td>
                            </tr>
                            <tr>
                                <td>정시 퇴근 시간</td>
                                <td>18:00</td>
                            </tr>
                            <tr>
                                <td>휴게(점심) 시간</td>
                                <td>12:00 ~ 13:00 (1시간)</td>
                            </tr>
                        </table>
                    </div>
                    <div class="card">
                        <div class="card-title">공지사항 및 안내</div>
                        <ul style="padding-left:1.2rem; font-size:0.9rem; line-height:1.6; color:var(--text-muted);">
                            <li>시스템에 등록된 모든 데이터는 실시간 반영됩니다.</li>
                            <li>근무시간 산정 규칙 변경 시 시스템 관리자에게 문의하세요.</li>
                            <li>휴가 신청은 [휴가 및 스케줄 관리] 메뉴에서 등록할 수 있습니다.</li>
                        </ul>
                    </div>
                </div>
            </section>

            <!-- 탭 2: 출퇴근 관리 -->
            <section id="tab-attendance" class="content-section">
                <div class="card">
                    <div class="card-title">출퇴근 기록 및 근무시간 이력</div>
                    <table>
                        <thead>
                            <tr>
                                <th>날짜</th>
                                <th>성명(ID)</th>
                                <th>실제 출근시각</th>
                                <th>산정 시작시각</th>
                                <th>퇴근시각</th>
                                <th>점심차감</th>
                                <th>총 인정 근무시간</th>
                            </tr>
                        </thead>
                        <tbody id="attendance-history-table">
                            <!-- JS dynamic row -->
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- 탭 3: 직원 계정 생성 및 관리 -->
            <section id="tab-employees" class="content-section">
                <div class="grid-2">
                    <div class="card">
                        <div class="card-title">신규 직원 계정 생성</div>
                        <form onsubmit="handleCreateEmployee(event)">
                            <div class="form-group">
                                <label>아이디</label>
                                <input type="text" id="emp-id" required placeholder="예: user01">
                            </div>
                            <div class="form-group">
                                <label>비밀번호</label>
                                <input type="password" id="emp-pw" required placeholder="비밀번호 입력">
                            </div>
                            <div class="form-group">
                                <label>이름</label>
                                <input type="text" id="emp-name" required placeholder="예: 홍길동">
                            </div>
                            <div class="form-group">
                                <label>부서</label>
                                <input type="text" id="emp-dept" required placeholder="예: 개발팀">
                            </div>
                            <div class="form-group">
                                <label>권한 역할</label>
                                <select id="emp-role">
                                    <option value="일반 직원">일반 직원</option>
                                    <option value="시스템 관리자">시스템 관리자</option>
                                </select>
                            </div>
                            <button type="submit" class="btn">직원 계정 생성</button>
                        </form>
                    </div>

                    <div class="card">
                        <div class="card-title">등록된 직원 목록</div>
                        <table>
                            <thead>
                                <th>아이디</th>
                                <th>이름</th>
                                <th>부서</th>
                                <th>권한</th>
                                <th>관리</th>
                            </thead>
                            <tbody id="employee-list-table">
                                <!-- JS dynamic row -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            <!-- 탭 4: 휴가 및 스케줄 관리 -->
            <section id="tab-schedule" class="content-section">
                <div class="grid-2">
                    <div class="card">
                        <div class="card-title">휴가 및 스케줄 신청</div>
                        <form onsubmit="handleApplyLeave(event)">
                            <div class="form-group">
                                <label>신청 유형</label>
                                <select id="leave-type">
                                    <option value="연차">연차</option>
                                    <option value="반차">반차</option>
                                    <option value="병가">병가</option>
                                    <option value="경조사">경조사</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>시작일</label>
                                <input type="date" id="leave-start" required>
                            </div>
                            <div class="form-group">
                                <label>종료일</label>
                                <input type="date" id="leave-end" required>
                            </div>
                            <div class="form-group">
                                <label>사유</label>
                                <textarea id="leave-reason" rows="3" placeholder="사유를 입력하세요"></textarea>
                            </div>
                            <button type="submit" class="btn">스케줄 등록 신청</button>
                        </form>
                    </div>

                    <div class="card">
                        <div class="card-title">휴가 신청 및 스케줄 현황</div>
                        <table>
                            <thead>
                                <tr>
                                    <th>신청자</th>
                                    <th>유형</th>
                                    <th>기간</th>
                                    <th>상태</th>
                                </tr>
                            </thead>
                            <tbody id="leave-list-table">
                                <!-- JS dynamic row -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            <!-- 탭 5: 시스템 관리 - 사용자 권한 관리 (모두 한국어 처리) -->
            <section id="tab-permissions" class="content-section">
                <div class="card">
                    <div class="card-title">시스템 사용자 권한 설정</div>
                    <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
                        각 역할 그룹별로 메뉴 접근 및 기능 실행 권한을 설정할 수 있습니다.
                    </p>
                    <table>
                        <thead>
                            <tr>
                                <th>역할 그룹 (Role)</th>
                                <th>접근 가능 메뉴 (Permissions)</th>
                                <th>출퇴근 버튼 권한</th>
                                <th>권한 수정</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>시스템 관리자 (Administrator)</strong></td>
                                <td>전체 메뉴 (대시보드, 출퇴근, 직원관리, 스케줄, 시스템관리)</td>
                                <td><span class="badge badge-success">전체 권한</span></td>
                                <td><button class="btn btn-secondary btn-inline" onclick="alert('시스템 관리자 권한은 기본 최고 권한입니다.')">수정</button></td>
                            </tr>
                            <tr>
                                <td><strong>일반 직원 (User)</strong></td>
                                <td>대시보드, 출퇴근 관리, 휴가/스케줄 신청</td>
                                <td><span class="badge badge-success">본인 출퇴근 가능</span></td>
                                <td><button class="btn btn-secondary btn-inline" onclick="alert('권한 설정 변경 모달이 호출됩니다.')">권한 변경</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

        </main>
    </div>

    <script>
        // --- 1. 초기 데이터 설정 (테스트 데이터 모두 제거, admin 1개만 남김) ---
        let users = [
            { id: 'admin', pw: 'admin123', name: '관리자', dept: '경영관리팀', role: '시스템 관리자' }
        ];

        let currentUser = null;

        // 출퇴근 이력 DB
        let attendanceRecords = [];

        // 휴가 신청 이력 DB
        let leaveRecords = [];

        // --- 2. 도쿄 기준 서버 시간 계산 및 타이머 ---
        function updateTokyoClock() {
            const now = new Date();
            // Asia/Tokyo 타임존으로 시각 변환
            const options = {
                timeZone: 'Asia/Tokyo',
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            };
            
            const formatter = new Intl.DateTimeFormat('ko-KR', options);
            const formattedParts = formatter.formatToParts(now);
            
            let y, m, d, hh, mm, ss;
            formattedParts.forEach(p => {
                if (p.type === 'year') y = p.value;
                if (p.type === 'month') m = p.value;
                if (p.type === 'day') d = p.value;
                if (p.type === 'hour') hh = p.value;
                if (p.type === 'minute') mm = p.value;
                if (p.type === 'second') ss = p.value;
            });

            const clockString = `${y}.${m}.${d}. ${hh}:${mm}:${ss} JST`;
            const dateBadgeString = `${y}-${m}-${d}`;

            document.getElementById('tokyo-clock').innerText = clockString;
            document.getElementById('today-date-badge').innerText = dateBadgeString;
        }

        setInterval(updateTokyoClock, 1000);
        updateTokyoClock();

        // --- 3. 로그인 / 로그아웃 처리 ---
        function handleLogin(e) {
            e.preventDefault();
            const inputId = document.getElementById('login-id').value.trim();
            const inputPw = document.getElementById('login-pw').value.trim();

            const found = users.find(u => u.id === inputId && u.pw === inputPw);

            if (found) {
                currentUser = found;
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('app-container').style.display = 'flex';
                document.getElementById('current-user-display').innerText = `${currentUser.name} (${currentUser.id})`;
                
                // 로그인 후 인터페이스 초기화
                renderTables();
                updateCommuteDisplay();
            } else {
                alert('아이디 또는 비밀번호가 올바르지 않습니다.');
            }
        }

        function handleLogout() {
            currentUser = null;
            document.getElementById('login-screen').style.display = 'flex';
            document.getElementById('app-container').style.display = 'none';
            document.getElementById('login-id').value = '';
            document.getElementById('login-pw').value = '';
        }

        // --- 4. 탭 전환 처리 ---
        function switchTab(tabName) {
            const navItems = document.querySelectorAll('.nav-item');
            navItems.forEach(item => item.classList.remove('active'));

            const sections = document.querySelectorAll('.content-section');
            sections.forEach(sec => sec.classList.remove('active'));

            const targetSection = document.getElementById(`tab-${tabName}`);
            if (targetSection) targetSection.classList.add('active');

            // 이벤트 타겟 액티브 효과
            event.currentTarget.classList.add('active');
        }

        // --- 5. 출퇴근 핵심 로직 ---
        // 규칙: 출근 누르면 실제 출근시간 기록, 계산은 09:00부터. 퇴근은 자유(18:00 정시). 점심시간 12~13시 차감.
        
        function getTodayString() {
            const options = { timeZone: 'Asia/Tokyo', year: 'numeric', month: '2-digit', day: '2-digit' };
            const parts = new Intl.DateTimeFormat('ko-KR', options).formatToParts(new Date());
            let y, m, d;
            parts.forEach(p => {
                if (p.type === 'year') y = p.value;
                if (p.type === 'month') m = p.value;
                if (p.type === 'day') d = p.value;
            });
            return `${y}-${m}-${d}`;
        }

        function getTokyoCurrentTime() {
            const options = { timeZone: 'Asia/Tokyo', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
            const parts = new Intl.DateTimeFormat('ko-KR', options).formatToParts(new Date());
            let hh, mm, ss;
            parts.forEach(p => {
                if (p.type === 'hour') hh = p.value;
                if (p.type === 'minute') mm = p.value;
                if (p.type === 'second') ss = p.value;
            });
            return { hh, mm, ss, timeStr: `${hh}:${mm}:${ss}` };
        }

        function processClockIn() {
            if (!currentUser) return;
            const today = getTodayString();
            const timeObj = getTokyoCurrentTime();

            let record = attendanceRecords.find(r => r.userId === currentUser.id && r.date === today);

            if (record && record.clockIn) {
                alert(`이미 오늘(${record.clockIn}) 출근 등록을 완료하셨습니다.`);
                return;
            }

            if (!record) {
                record = {
                    date: today,
                    userId: currentUser.id,
                    userName: currentUser.name,
                    clockIn: timeObj.timeStr,
                    clockOut: '--:--:--',
                    calculatedHoursStr: '근무 중'
                };
                attendanceRecords.push(record);
            } else {
                record.clockIn = timeObj.timeStr;
            }

            alert(`출근 등록이 완료되었습니다. (실제 출근시각: ${timeObj.timeStr} / 인정 시작시각: 09:00:00)`);
            updateCommuteDisplay();
            renderTables();
        }

        function processClockOut() {
            if (!currentUser) return;
            const today = getTodayString();
            const timeObj = getTokyoCurrentTime();

            let record = attendanceRecords.find(r => r.userId === currentUser.id && r.date === today);

            if (!record || !record.clockIn) {
                alert('출근 기록이 없습니다. 먼저 출근 버튼을 눌러주세요.');
                return;
            }

            record.clockOut = timeObj.timeStr;
            record.calculatedHoursStr = calculateWorkedHours(record.clockIn, record.clockOut);

            alert(`퇴근 등록이 완료되었습니다. (퇴근시각: ${timeObj.timeStr})`);
            updateCommuteDisplay();
            renderTables();
        }

        // 근무시간 산정 공식
        // 계산 시작: 무조건 09:00 고정
        // 점심시간: 12:00 ~ 13:00 (1시간 자동 차감)
        function calculateWorkedHours(clockInStr, clockOutStr) {
            if (!clockOutStr || clockOutStr === '--:--:--') return '근무 중';

            // 퇴근 시각 분해
            const [outH, outM] = clockOutStr.split(':').map(Number);
            
            // 인정 시작시간 = 09:00
            const startH = 9;
            const startM = 0;

            let startMinutes = startH * 60 + startM; // 540분
            let endMinutes = outH * 60 + outM;

            if (endMinutes <= startMinutes) {
                return '0시간 0분';
            }

            let totalMinutes = endMinutes - startMinutes;

            // 점심시간 (12:00 ~ 13:00) 차감 여부 계산
            // 12:00 (720분) 이후까지 근무한 경우 점심 1시간(60분) 차감
            if (endMinutes >= 780) { // 13:00 이후 퇴근
                totalMinutes -= 60;
            } else if (endMinutes > 720) { // 12:00 ~ 13:00 사이 퇴근
                let lunchOverlap = endMinutes - 720;
                totalMinutes -= lunchOverlap;
            }

            if (totalMinutes < 0) totalMinutes = 0;

            const workH = Math.floor(totalMinutes / 60);
            const workM = totalMinutes % 60;

            return `${workH}시간 ${workM}분`;
        }

        function updateCommuteDisplay() {
            if (!currentUser) return;
            const today = getTodayString();
            const record = attendanceRecords.find(r => r.userId === currentUser.id && r.date === today);

            if (record) {
                document.getElementById('display-clock-in').innerText = record.clockIn || '--:--:--';
                document.getElementById('display-clock-out').innerText = record.clockOut || '--:--:--';
                document.getElementById('display-work-hours').innerText = record.calculatedHoursStr || '0시간 0분';
            } else {
                document.getElementById('display-clock-in').innerText = '--:--:--';
                document.getElementById('display-clock-out').innerText = '--:--:--';
                document.getElementById('display-work-hours').innerText = '0시간 0분';
            }
        }

        // --- 6. 직원 등록 및 휴가 신청 ---
        function handleCreateEmployee(e) {
            e.preventDefault();
            const id = document.getElementById('emp-id').value.trim();
            const pw = document.getElementById('emp-pw').value.trim();
            const name = document.getElementById('emp-name').value.trim();
            const dept = document.getElementById('emp-dept').value.trim();
            const role = document.getElementById('emp-role').value;

            if (users.find(u => u.id === id)) {
                alert('이미 존재인 아이디입니다.');
                return;
            }

            users.push({ id, pw, name, dept, role });
            alert(`신규 직원 [${name}] 계정이 성공적으로 생성되었습니다.`);

            document.getElementById('emp-id').value = '';
            document.getElementById('emp-pw').value = '';
            document.getElementById('emp-name').value = '';
            document.getElementById('emp-dept').value = '';

            renderTables();
        }

        function deleteEmployee(userId) {
            if (userId === 'admin') {
                alert('기본 관리자 계정(admin)은 삭제할 수 없습니다.');
                return;
            }
            if (confirm(`정말 ${userId} 계정을 삭제하시겠습니까?`)) {
                users = users.filter(u => u.id !== userId);
                renderTables();
            }
        }

        function handleApplyLeave(e) {
            e.preventDefault();
            const type = document.getElementById('leave-type').value;
            const start = document.getElementById('leave-start').value;
            const end = document.getElementById('leave-end').value;
            const reason = document.getElementById('leave-reason').value;

            leaveRecords.push({
                applicant: currentUser.name,
                type,
                period: `${start} ~ ${end}`,
                status: '승인 대기'
            });

            alert('휴가 신청이 완료되었습니다.');
            document.getElementById('leave-start').value = '';
            document.getElementById('leave-end').value = '';
            document.getElementById('leave-reason').value = '';

            renderTables();
        }

        // --- 7. 화면 테이블 렌더링 ---
        function renderTables() {
            // 1) 출퇴근 기록 테이블
            const attTbody = document.getElementById('attendance-history-table');
            attTbody.innerHTML = '';
            if (attendanceRecords.length === 0) {
                attTbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#94a3b8;">출퇴근 기록이 없습니다.</td></tr>`;
            } else {
                attendanceRecords.forEach(r => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${r.date}</td>
                        <td>${r.userName}(${r.userId})</td>
                        <td>${r.clockIn}</td>
                        <td><span class="badge badge-warning">09:00:00 (고정)</span></td>
                        <td>${r.clockOut}</td>
                        <td>1시간 (12~13시)</td>
                        <td><strong>${r.calculatedHoursStr}</strong></td>
                    `;
                    attTbody.appendChild(tr);
                });
            }

            // 2) 직원 목록 테이블
            const empTbody = document.getElementById('employee-list-table');
            empTbody.innerHTML = '';
            users.forEach(u => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${u.id}</td>
                    <td>${u.name}</td>
                    <td>${u.dept}</td>
                    <td><span class="badge ${u.role === '시스템 관리자' ? 'badge-danger' : 'badge-success'}">${u.role}</span></td>
                    <td>
                        ${u.id !== 'admin' ? `<button class="btn btn-secondary btn-inline" onclick="deleteEmployee('${u.id}')" style="background:#ef4444;">삭제</button>` : '-'}
                    </td>
                `;
                empTbody.appendChild(tr);
            });

            // 3) 휴가 신청 테이블
            const leaveTbody = document.getElementById('leave-list-table');
            leaveTbody.innerHTML = '';
            if (leaveRecords.length === 0) {
                leaveTbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#94a3b8;">신청된 휴가 내역이 없습니다.</td></tr>`;
            } else {
                leaveRecords.forEach(l => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${l.applicant}</td>
                        <td>${l.type}</td>
                        <td>${l.period}</td>
                        <td><span class="badge badge-warning">${l.status}</span></td>
                    `;
                    leaveTbody.appendChild(tr);
                });
            }
        }
    </script>
</body>
</html>
