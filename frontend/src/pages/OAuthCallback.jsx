
import React, { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

export default function OAuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const code = searchParams.get('code');
    if (!code) {
      // 에러 처리
      alert('인가 코드가 없습니다');
      navigate('/login');
      return;
    }

    // 백엔드에 code 전송하여 토큰 받기
    fetch('http://localhost:8000/auth/kakao/callback?code=' + code)
      .then(res => res.json())
      .then(data => {
        // 예: 로컬 스토리지에 저장
        localStorage.setItem('access_token', data.access_token);
        // 메인 페이지 이동
        navigate('/');
      })
      .catch(err => {
        console.error(err);
        alert('로그인 중 오류가 발생했습니다');
        navigate('/login');
      });
  }, [searchParams, navigate]);

  return (
    <div style={{
      display:'flex', alignItems:'center', justifyContent:'center',
      height:'100vh'
    }}>
      <p>로그인 처리 중…</p>
    </div>
  );
}