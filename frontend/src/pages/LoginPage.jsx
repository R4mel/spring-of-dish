import React from 'react';

export default function LoginPage() {
  const REST_API_KEY = import.meta.env.VITE_KAKAO_CLIENT_ID;
  const REDIRECT_URI = import.meta.env.VITE_REDIRECT_URI;

  const handleKakaoLogin = () => {
    const kakaoAuthUrl =
      `https://kauth.kakao.com/oauth/authorize` +
      `?client_id=${REST_API_KEY2}` +
      `&redirect_uri=${encodeURIComponent(REDIRECT_URI)}` +
      `&response_type=code`;
    window.location.href = kakaoAuthUrl;
  };

  return (
    <div style={{ textAlign: 'center', marginTop: 100 }}>
      <h1>로그인</h1>
      <button
        onClick={handleKakaoLogin}
        style={{
          background: '#FEE500',
          border: 'none',
          padding: '12px 24px',
          fontSize: 16,
          cursor: 'pointer',
          borderRadius: 4
        }}
      >
        카카오로 시작하기
      </button>
    </div>
  );
}