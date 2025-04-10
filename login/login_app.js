import React, { useState, useMemo } from 'react';

function App() {
  // 날짜 상태: "YYYY-MM-DD" 형식으로 저장 (수정 가능)
  const [addedDate, setAddedDate] = useState("2025-04-02");
  const [expiryDate, setExpiryDate] = useState("2025-09-10");
  // 냉동 상태: false (일반 보관; 날짜 수정 가능) / true (냉동 보관; 날짜 수정 불가능)
  const [isFrozen, setIsFrozen] = useState(false);

  // 냉동 상태에 따라 소비기한(만료일)을 계산: 냉동이면 5개월 연장
  const displayedExpiryDate = useMemo(() => {
    if (!expiryDate) return new Date();
    const dt = new Date(expiryDate);
    if (isFrozen) {
      dt.setMonth(dt.getMonth() + 5);
    }
    return dt;
  }, [expiryDate, isFrozen]);

  // 추가된 날짜 객체
  const addedDateObj = useMemo(() => new Date(addedDate), [addedDate]);

  // D-Day 계산 (냉동 상태가 아닐 때만 계산; 냉동이면 "냉동"으로 표시)
  const dayDiff = useMemo(() => {
    if (isFrozen) return null;
    return Math.floor(
      (displayedExpiryDate.getTime() - addedDateObj.getTime()) / (1000 * 60 * 60 * 24)
    );
  }, [displayedExpiryDate, addedDateObj, isFrozen]);

  // 날짜를 "YYYY.MM.DD" 형태로 포맷하는 함수
  function formatDate(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}.${m}.${d}`;
  }

  // 냉동 상태 토글
  const handleFreezeClick = () => {
    setIsFrozen((prev) => !prev);
  };

  // 냉동보관 버튼 스타일: 냉동이면 파란색, 아닐 때는 검정색 (흑백TV 느낌)
  const freezeButtonStyle = {
    width: 60,
    height: 60,
    borderRadius: '50%',
    backgroundColor: isFrozen ? '#0000FF' : '#000000',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#fff',
    fontSize: '28px',
    border: 'none',
    cursor: 'pointer',
    outline: 'none',
    transition: 'background-color 0.3s ease',
  };

  return (
    <div
      style={{
        fontFamily: 'Arial, sans-serif',
        backgroundColor: '#F5F5F5',
        minHeight: '100vh',
        padding: '20px',
      }}
    >
      {/* 상단 헤더 */}
      <header
        style={{
          backgroundColor: '#A0D96C',
          color: '#fff',
          padding: '15px',
          textAlign: 'center',
          borderRadius: '8px',
          marginBottom: '20px',
        }}
      >
        <h1 style={{ margin: 0 }}>홈</h1>
      </header>

      {/* 중앙 카드 영역 */}
      <div
        style={{
          backgroundColor: '#fff',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          padding: '20px',
          maxWidth: '400px',
          margin: '0 auto',
        }}
      >
        {/* 제품 정보 영역 */}
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
          <img
            src="https://via.placeholder.com/80"
            alt="대파"
            style={{ borderRadius: '8px', marginRight: '15px' }}
          />
          <div>
            <h2 style={{ margin: '0 0 5px 0', fontSize: '20px' }}>
              대파{' '}
              <span
                style={{
                  color: isFrozen ? '#0000FF' : (dayDiff < 0 ? 'red' : '#333'),
                  fontWeight: 'bold',
                  fontSize: '16px',
                }}
              >
                {isFrozen ? '냉동' : `D-${dayDiff}`}
              </span>
            </h2>
          </div>
        </div>

        {/* 날짜 정보 영역 */}
        <div style={{ marginBottom: '15px', fontSize: '14px', lineHeight: 1.6 }}>
          {/* 추가된 날짜 영역 */}
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
            <p style={{ margin: 0, flex: 1 }}>
              <strong>추가된 날짜:</strong> {formatDate(new Date(addedDate))}
            </p>
            <input
              type="date"
              value={addedDate}
              onChange={(e) => setAddedDate(e.target.value)}
              disabled={isFrozen}
              style={{ marginRight: '8px' }}
            />
          </div>

          {/* 소비기한 마감 영역 */}
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <p style={{ margin: 0, flex: 1 }}>
              <strong>소비기한 마감:</strong> {formatDate(displayedExpiryDate)}
            </p>
            <input
              type="date"
              value={expiryDate}
              onChange={(e) => setExpiryDate(e.target.value)}
              disabled={isFrozen}
              style={{ marginRight: '8px' }}
            />
          </div>
        </div>

        {/* 냉동보관 버튼 영역 */}
        <div style={{ textAlign: 'center', marginTop: '20px' }}>
          <button style={freezeButtonStyle} onClick={handleFreezeClick}>
            ❄️
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;

