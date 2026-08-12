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
            margin-bottom: 1rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.3rem;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 0.65rem;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-size: 0.9rem;
        }

        .form-row {
            display: flex;
            gap: 1rem;
        }

        .form-row .form-group {
            flex: 1;
        }

        .btn {
            display: inline-block;
            width: 100%;
            padding: 0.75rem;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 0.95rem;
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
            padding: 0.4rem 0.8rem;
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
            flex-shrink: 0;
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
            overflow-y: auto;
        }

        .nav-item {
            padding: 0.85rem 1.5rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            font-size: 0.9rem;
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

        /* 대시보드 상단 히어로 카드 */
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
            font-size: 0.85rem;
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
            font-size: 0.95rem;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: transform 0.1s;
        }
        .btn-commute:active {
            transform: scale(0.97);
        }

        .btn-in { background-color: var(--success-color); color: white; }
        .btn-out { background-color: var(--danger-color); color: white; }

        .rules-note {
            font-size: 0.8rem;
            color: #94a3b8;
            margin-top: 0.75rem;
            line-height: 1.4;
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

        .table-container {
            width: 100%;
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 0.5rem;
            font-size: 0.85rem;
        }

        th, td {
            padding: 0.7rem 0.8rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }

        th {
            background-color: #f1f5f9;
            font-weight: 600;
            color: var(--text-muted);
        }

        .badge {
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge-success { background: #d1fae5; color: #065f46; }
        .badge-warning { background: #fef3c7; color: #92400e; }
        .badge-danger  { background: #fee2e2; color: #991b1b; }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }

        @media (max-width: 1024px) {
            .grid-2 { grid-template-columns: 1fr; }
            #app-container { flex-direction: column; }
            sidebar { width: 100%; }
        }
    </style>
</head>
<body>

    <!-- 1. 로그인 화면 (테스트 계정 안내창 전면 제거) -->
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
                <li class="nav-item" onclick="switchTab('product-master')">마스터 상품 등록/관리</li>
                <li class="nav-item" onclick="switchTab('purchase-order')">발주 등록/관리</li>
                <li class="nav-item" onclick="switchTab('employees')">직원 계정 생성/관리</li>
                <li class="nav-item" onclick="switchTab('schedule')">휴가 및 스케줄 관리</li>
                <li class="nav-item" onclick="switchTab('permissions')">시스템 관리 (사용자 권한)</li>
            </ul>
            <div class="user-info">
                <span id="current-user-display">관리자 (admin)</span>
                <button class="btn btn-secondary btn-inline" onclick="handleLogout()" style="font-size:0.75rem;">로그아웃</button>
            </div>
        </sidebar>

        <!-- 메인 콘텐츠 영역 -->
        <main>

            <!-- 로그인 후 첫 화면 최상단 도쿄 기준 서버시간 & 출퇴근 위젯 -->
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
                        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">현재 접속 중인 계정의 오늘 출퇴근 및 근무시간 규칙 안내입니다.</p>
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
                                <td>12:00 ~ 13:00 (1시간 자동 차감)</td>
                            </tr>
                        </table>
                    </div>
                    <div class="card">
                        <div class="card-title">시스템 주요 현황</div>
                        <ul style="padding-left:1.2rem; font-size:0.85rem; line-height:1.8; color:var(--text-muted);">
                            <li>마스터 상품 및 상세정보를 수시로 등록/관리할 수 있습니다.</li>
                            <li>발주 등록 시 상세 수량, 단가, 납기일, 입고 창고 등을 지정합니다.</li>
                            <li>시스템 문의는 관리자 계정(`admin`)을 통해 가능합니다.</li>
                        </ul>
                    </div>
                </div>
            </section>

            <!-- 탭 2: 출퇴근 관리 -->
            <section id="tab-attendance" class="content-section">
                <div class="card">
                    <div class="card-title">출퇴근 이력 및 근무시간 조회</div>
                    <div class="table-container">
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
                            <tbody id="attendance-history-table"></tbody>
                        </table>
                    </div>
                </div>
            </section>

            <!-- 탭 3: 마스터 상품 등록/관리 (상세 정보 포함) -->
            <section id="tab-product-master" class="content-section">
                <div class="grid-2">
                    <div class="card">
                        <div class="card-title">마스터 상품 및 상세 정보 등록</div>
                        <form onsubmit="handleRegisterProduct(event)">
                            <div class="form-row">
                                <div class="form-group">
                                    <label>상품 코드 *</label>
                                    <input type="text" id="prod-code" required placeholder="예: PRD-1001">
                                </div>
                                <div class="form-group">
                                    <label>상품명 *</label>
                                    <input type="text" id="prod-name" required placeholder="예: 사무용 모니터 27인치">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>카테고리</label>
                                    <select id="prod-category">
                                        <option value="전자기기">전자기기</option>
                                        <option value="사무용품">사무용품</option>
                                        <option value="소모품">소모품</option>
                                        <option value="가구/집기">가구/집기</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>규격 / 단위</label>
                                    <input type="text" id="prod-unit" placeholder="예: EA, Box, Set">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>기본 단가 (원)</label>
                                    <input type="number" id="prod-price" required placeholder="예: 250000">
                                </div>
                                <div class="form-group">
                                    <label>적정 재고량</label>
                                    <input type="number" id="prod-stock-target" placeholder="예: 50">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>제조사 / 공급업체</label>
                                    <input type="text" id="prod-vendor" placeholder="예: 삼성전자 / 알파유통">
                                </div>
                                <div class="form-group">
                                    <label>원산지</label>
                                    <input type="text" id="prod-origin" placeholder="예: 국산, 중국 등">
                                </div>
                            </div>
                            <div class="form-group">
                                <label>바코드 / 식별 번호</label>
                                <input type="text" id="prod-barcode" placeholder="예: 8801234567890">
                            </div>
                            <div class="form-group">
                                <label>상세 설명 및 특이사항</label>
                                <textarea id="prod-desc" rows="3" placeholder="상품에 대한 상세 정보 및 보관 유의사항 입력"></textarea>
                            </div>
                            <button type="submit" class="btn">마스터 상품 등록</button>
                        </form>
                    </div>

                    <div class="card">
                        <div class="card-title">등록된 마스터 상품 목록</div>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>코드</th>
                                        <th>상품명</th>
                                        <th>카테고리</th>
                                        <th>기본단가</th>
                                        <th>공급업체</th>
                                        <th>바코드/상세</th>
                                    </tr>
                                </thead>
                                <tbody id="product-master-table"></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 탭 4: 발주 등록/관리 (상세 정보 포함) -->
            <section id="tab-purchase-order" class="content-section">
                <div class="grid-2">
                    <div class="card">
                        <div class="card-title">발주 상세 정보 등록</div>
                        <form onsubmit="handleRegisterOrder(event)">
                            <div class="form-group">
                                <label>발주 대상 마스터 상품 선택 *</label>
                                <select id="po-product-select" onchange="onSelectOrderProduct(this)" required>
                                    <option value="">-- 마스터 상품을 선택하세요 --</option>
                                </select>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>발주처 / 공급업체 *</label>
                                    <input type="text" id="po-vendor" required placeholder="선택 시 자동 입력 또는 직접입력">
                                </div>
                                <div class="form-group">
                                    <label>입고 예정 창고</label>
                                    <select id="po-warehouse">
                                        <option value="제1메인물류센터">제1메인물류센터</option>
                                        <option value="제2부자재창고">제2부자재창고</option>
                                        <option value="본사 사무실">본사 사무실</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>발주 수량 *</label>
                                    <input type="number" id="po-qty" oninput="calculatePoTotal()" required placeholder="수량 입력">
                                </div>
                                <div class="form-group">
                                    <label>발주 단가 (원) *</label>
                                    <input type="number" id="po-unit-price" oninput="calculatePoTotal()" required placeholder="단가 입력">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>총 발주 금액 (자동계산)</label>
                                    <input type="text" id="po-total-price" readonly style="background:#f1f5f9; font-weight:bold; color:var(--primary-color);" value="0 원">
                                </div>
                                <div class="form-group">
                                    <label>납기 요청일 *</label>
                                    <input type="date" id="po-delivery-date" required>
                                </div>
                            </div>
                            <div class="form-group">
                                <label>발주 담당자</label>
                                <input type="text" id="po-manager" placeholder="담당자 이름">
                            </div>
                            <div class="form-group">
                                <label>상세 요청사항 및 비고</label>
                                <textarea id="po-notes" rows="3" placeholder="포장 상태 요청, 배송 시 주의사항 등 입력"></textarea>
                            </div>
                            <button type="submit" class="btn">발주 등록 완료</button>
                        </form>
                    </div>

                    <div class="card">
                        <div class="card-title">발주 등록 현황 및 상세 조회</div>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>발주번호</th>
                                        <th>상품명</th>
                                        <th>공급업체</th>
                                        <th>수량</th>
                                        <th>총액</th>
                                        <th>납기요청일</th>
                                        <th>상태</th>
                                    </tr>
                                </thead>
                                <tbody id="purchase-order-table"></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 탭 5: 직원 계정 생성 및 관리 -->
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
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>아이디</th>
                                        <th>이름</th>
                                        <th>부서</th>
                                        <th>권한</th>
                                        <th>관리</th>
                                    </tr>
                                </thead>
                                <tbody id="employee-list-table"></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 탭 6: 휴가 및 스케줄 관리 -->
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
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>신청자</th>
                                        <th>유형</th>
                                        <th>기간</th>
                                        <th>상태</th>
                                    </tr>
                                </thead>
                                <tbody id="leave-list-table"></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 탭 7: 시스템 관리 - 사용자 권한 관리 (전체 한글화 완료) -->
            <section id="tab-permissions" class="content-section">
                <div class="card">
                    <div class="card-title">시스템 사용자 권한 설정</div>
                    <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
                        각 역할 그룹별로 메뉴 접근 및 기능 실행 권한을 한국어로 명확히 관리합니다.
                    </p>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>역할 그룹</th>
                                    <th>접근 가능 메뉴 권한</th>
                                    <th>출퇴근 기능 권한</th>
                                    <th>권한 수정</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>시스템 관리자 (Administrator)</strong></td>
                                    <td>전체 메뉴 (대시보드, 출퇴근, 마스터상품, 발주관리, 직원관리, 스케줄, 시스템관리)</td>
                                    <td><span class="badge badge-success">전체 권한</span></td>
                                    <td><button class="btn btn-secondary btn-inline" onclick="alert('최고 관리자 권한은 기본 설정 상태입니다.')">수정</button></td>
                                </tr>
                                <tr>
                                    <td><strong>일반 직원 (User)</strong></td>
                                    <td>대시보드, 출퇴근 관리, 마스터 조회, 발주 등록, 휴가 신청</td>
                                    <td><span class="badge badge-success">본인 출퇴근 가능</span></td>
                                    <td><button class="btn btn-secondary btn-inline" onclick="alert('권한 설정 모달이 호출됩니다.')">권한 변경</button></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

        </main>
    </div>

    <script>
        // --- 1. 초기 데이터 설정 (admin 계정 1개만 유일하게 남김) ---
        let users = [
            { id: 'admin', pw: 'admin123', name: '관리자', dept: '경영관리팀', role: '시스템 관리자' }
        ];

        let currentUser = null;

        // 마스터 상품 데이터 저장소
        let masterProducts = [];

        // 발주 등록 데이터 저장소
        let purchaseOrders = [];

        // 출퇴근 기록 저장소
        let attendanceRecords = [];

        // 휴가/스케줄 기록 저장소
        let leaveRecords = [];

        // --- 2. 도쿄 기준 서버 시간 타이머 (Asia/Tokyo) ---
        function updateTokyoClock() {
            const now = new Date();
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

            document.getElementById('tokyo-clock').innerText = `${y}.${m}.${d}. ${hh}:${mm}:${ss} JST`;
            document.getElementById('today-date-badge').innerText = `${y}-${m}-${d}`;
        }

        setInterval(updateTokyoClock, 1000);
        updateTokyoClock();

        // --- 3. 로그인 및 로그아웃 ---
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
                
                // 로그인 후 담당자 필드 초기 세팅
                document.getElementById('po-manager').value = currentUser.name;

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

        // --- 4. 탭 전환 ---
        function switchTab(tabName) {
            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
            document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));

            const targetSection = document.getElementById(`tab-${tabName}`);
            if (targetSection) targetSection.classList.add('active');

            event.currentTarget.classList.add('active');
        }

        // --- 5. 출퇴근 처리 (규칙: 09시 고정 시작, 18시 정시퇴근, 12-13시 점심 차감) ---
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
            return `${hh}:${mm}:${ss}`;
        }

        function processClockIn() {
            if (!currentUser) return;
            const today = getTodayString();
            const nowTime = getTokyoCurrentTime();

            let record = attendanceRecords.find(r => r.userId === currentUser.id && r.date === today);

            if (record && record.clockIn) {
                alert(`이미 오늘(${record.clockIn}) 출근 등록 완료되었습니다.`);
                return;
            }

            if (!record) {
                record = {
                    date: today,
                    userId: currentUser.id,
                    userName: currentUser.name,
                    clockIn: nowTime,
                    clockOut: '--:--:--',
                    calculatedHoursStr: '근무 중'
                };
                attendanceRecords.push(record);
            } else {
                record.clockIn = nowTime;
            }

            alert(`출근 완료! (실제 기록: ${nowTime} / 인정 시작: 09:00:00)`);
            updateCommuteDisplay();
            renderTables();
        }

        function processClockOut() {
            if (!currentUser) return;
            const today = getTodayString();
            const nowTime = getTokyoCurrentTime();

            let record = attendanceRecords.find(r => r.userId === currentUser.id && r.date === today);

            if (!record || !record.clockIn) {
                alert('출근 기록이 존재하지 않습니다. 먼저 출근을 눌러주세요.');
                return;
            }

            record.clockOut = nowTime;
            record.calculatedHoursStr = calculateWorkedHours(record.clockIn, record.clockOut);

            alert(`퇴근 완료! (퇴근시각: ${nowTime})`);
            updateCommuteDisplay();
            renderTables();
        }

        function calculateWorkedHours(clockInStr, clockOutStr) {
            if (!clockOutStr || clockOutStr === '--:--:--') return '근무 중';

            const [outH, outM] = clockOutStr.split(':').map(Number);
            
            // 기준 09:00 (540분)
            let startMinutes = 9 * 60;
            let endMinutes = outH * 60 + outM;

            if (endMinutes <= startMinutes) return '0시간 0분';

            let totalMinutes = endMinutes - startMinutes;

            // 점심시간 12:00~13:00 차감
            if (endMinutes >= 780) { // 13:00 이후
                totalMinutes -= 60;
            } else if (endMinutes > 720) { // 12:00 ~ 13:00 사이
                totalMinutes -= (endMinutes - 720);
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

        // --- 6. 마스터 상품 등록 / 관리 ---
        function handleRegisterProduct(e) {
            e.preventDefault();
            const code = document.getElementById('prod-code').value.trim();
            const name = document.getElementById('prod-name').value.trim();
            const category = document.getElementById('prod-category').value;
            const unit = document.getElementById('prod-unit').value.trim();
            const price = Number(document.getElementById('prod-price').value);
            const stockTarget = document.getElementById('prod-stock-target').value;
            const vendor = document.getElementById('prod-vendor').value.trim();
            const origin = document.getElementById('prod-origin').value.trim();
            const barcode = document.getElementById('prod-barcode').value.trim();
            const desc = document.getElementById('prod-desc').value.trim();

            if (masterProducts.find(p => p.code === code)) {
                alert('이미 존재인 상품 코드입니다.');
                return;
            }

            const newProduct = { code, name, category, unit, price, stockTarget, vendor, origin, barcode, desc };
            masterProducts.push(newProduct);

            alert(`마스터 상품 [${name}] 등록이 완료되었습니다.`);

            // 폼 초기화
            document.getElementById('prod-code').value = '';
            document.getElementById('prod-name').value = '';
            document.getElementById('prod-unit').value = '';
            document.getElementById('prod-price').value = '';
            document.getElementById('prod-stock-target').value = '';
            document.getElementById('prod-vendor').value = '';
            document.getElementById('prod-origin').value = '';
            document.getElementById('prod-barcode').value = '';
            document.getElementById('prod-desc').value = '';

            updateProductSelectOptions();
            renderTables();
        }

        function updateProductSelectOptions() {
            const select = document.getElementById('po-product-select');
            select.innerHTML = '<option value="">-- 마스터 상품을 선택하세요 --</option>';
            masterProducts.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.code;
                opt.innerText = `[${p.code}] ${p.name} (${p.price.toLocaleString()}원)`;
                select.appendChild(opt);
            });
        }

        function onSelectOrderProduct(selectElem) {
            const code = selectElem.value;
            const prod = masterProducts.find(p => p.code === code);
            if (prod) {
                document.getElementById('po-vendor').value = prod.vendor || '';
                document.getElementById('po-unit-price').value = prod.price || 0;
                calculatePoTotal();
            }
        }

        // --- 7. 발주 등록 / 관리 ---
        function calculatePoTotal() {
            const qty = Number(document.getElementById('po-qty').value) || 0;
            const price = Number(document.getElementById('po-unit-price').value) || 0;
            const total = qty * price;
            document.getElementById('po-total-price').value = total.toLocaleString() + ' 원';
        }

        function handleRegisterOrder(e) {
            e.preventDefault();
            const prodCode = document.getElementById('po-product-select').value;
            const prod = masterProducts.find(p => p.code === prodCode);

            if (!prod) {
                alert('마스터 상품을 선택해주세요.');
                return;
            }

            const vendor = document.getElementById('po-vendor').value.trim();
            const warehouse = document.getElementById('po-warehouse').value;
            const qty = Number(document.getElementById('po-qty').value);
            const unitPrice = Number(document.getElementById('po-unit-price').value);
            const deliveryDate = document.getElementById('po-delivery-date').value;
            const manager = document.getElementById('po-manager').value.trim() || currentUser.name;
            const notes = document.getElementById('po-notes').value.trim();

            const orderNo = 'PO-' + Date.now().toString().slice(-6);

            const newOrder = {
                orderNo,
                prodCode: prod.code,
                prodName: prod.name,
                vendor,
                warehouse,
                qty,
                unitPrice,
                totalPrice: qty * unitPrice,
                deliveryDate,
                manager,
                notes,
                status: '발주 요청 완료'
            };

            purchaseOrders.push(newOrder);
            alert(`발주 등록 완료 (발주번호: ${orderNo})`);

            // 폼 초기화
            document.getElementById('po-product-select').value = '';
            document.getElementById('po-vendor').value = '';
            document.getElementById('po-qty').value = '';
            document.getElementById('po-unit-price').value = '';
            document.getElementById('po-total-price').value = '0 원';
            document.getElementById('po-delivery-date').value = '';
            document.getElementById('po-notes').value = '';

            renderTables();
        }

        // --- 8. 직원 및 휴가 신청 ---
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

            leaveRecords.push({
                applicant: currentUser.name,
                type,
                period: `${start} ~ ${end}`,
                status: '승인 대기'
            });

            alert('휴가 신청이 등록되었습니다.');
            document.getElementById('leave-start').value = '';
            document.getElementById('leave-end').value = '';
            document.getElementById('leave-reason').value = '';

            renderTables();
        }

        // --- 9. 화면 테이블 전체 렌더링 ---
        function renderTables() {
            // 1) 출퇴근 기록
            const attTbody = document.getElementById('attendance-history-table');
            attTbody.innerHTML = '';
            if (attendanceRecords.length === 0) {
                attTbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#94a3b8;">출퇴근 기록이 존재하지 않습니다.</td></tr>`;
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

            // 2) 마스터 상품 목록
            const prodTbody = document.getElementById('product-master-table');
            prodTbody.innerHTML = '';
            if (masterProducts.length === 0) {
                prodTbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#94a3b8;">등록된 마스터 상품이 없습니다.</td></tr>`;
            } else {
                masterProducts.forEach(p => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${p.code}</strong></td>
                        <td>${p.name}</td>
                        <td>${p.category}</td>
                        <td>${p.price.toLocaleString()}원</td>
                        <td>${p.vendor || '-'}</td>
                        <td><button class="btn btn-secondary btn-inline" onclick="alert('바코드: ${p.barcode || '없음'}\\n제조사/원산지: ${p.vendor || '-'}/${p.origin || '-'}\\n설명: ${p.desc || '없음'}')">상세보기</button></td>
                    `;
                    prodTbody.appendChild(tr);
                });
            }

            // 3) 발주 목록
            const poTbody = document.getElementById('purchase-order-table');
            poTbody.innerHTML = '';
            if (purchaseOrders.length === 0) {
                poTbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#94a3b8;">등록된 발주 내역이 없습니다.</td></tr>`;
            } else {
                purchaseOrders.forEach(po => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${po.orderNo}</strong></td>
                        <td>${po.prodName}</td>
                        <td>${po.vendor}</td>
                        <td>${po.qty}</td>
                        <td>${po.totalPrice.toLocaleString()}원</td>
                        <td>${po.deliveryDate}</td>
                        <td><span class="badge badge-success">${po.status}</span></td>
                    `;
                    poTbody.appendChild(tr);
                });
            }

            // 4) 직원 목록
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

            // 5) 휴가 신청 목록
            const leaveTbody = document.getElementById('leave-list-table');
            leaveTbody.innerHTML = '';
            if (leaveRecords.length === 0) {
                leaveTbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#94a3b8;">신청 내역이 없습니다.</td></tr>`;
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
