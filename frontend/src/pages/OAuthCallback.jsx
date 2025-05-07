import React, { useEffect, useContext } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

export default function OAuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);
  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    const code = searchParams.get('code');
    if (!code) {
      alert('인가 코드가 없습니다');
      navigate('/login');
      return;
    }

    // 1) 코드로 액세스 토큰 교환
    fetch(`${API_URL}/auth/kakao/callback?code=${code}`)
      .then(res => {
        if (!res.ok) throw new Error('토큰 교환 실패');
        return res.json();
      })
      .then(({ access_token }) => {
        localStorage.setItem('access_token', access_token);
        // 2) 토큰으로 프로필 조회
        return fetch(`${API_URL}/profile`, {
          headers: {
            Authorization: `Bearer ${access_token}`,
          },
        });
      })
      .then(res => {
        if (!res.ok) throw new Error('프로필 조회 실패');
        return res.json();
      })
      .then(profile => {
        login(profile);
        // 프로필을 필요한 곳에 저장 (예: Context, redux, localStorage…)
        console.log('사용자 정보:', profile);
        navigate('/');
      })
      .catch(err => {
        console.error(err);
        alert('로그인 처리 중 오류가 발생했습니다');
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