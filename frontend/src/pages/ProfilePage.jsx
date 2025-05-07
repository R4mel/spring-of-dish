// src/pages/ProfilePage.jsx
import React, { useEffect, useState } from 'react';

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const API_URL = import.meta.env.VITE_API_URL;      // ex) http://localhost:8000
  const token   = localStorage.getItem('access_token'); // 1) 로그인 후 저장해 둔 JWT

  useEffect(() => {
    if (!token) return;

    fetch(`${API_URL}/profile`, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,       // 2) Bearer 헤더에 토큰 추가
      },
    })
      .then(res => {
        if (!res.ok) throw new Error('프로필 조회 실패');
        return res.json();
      })
      .then(data => {
        setProfile(data);                          // 3) state에 저장
      })
      .catch(err => {
        console.error(err);
      });
  }, [API_URL, token]);

  if (!token) {
    return <p>로그인이 필요합니다.</p>;
  }

  if (!profile) {
    return <p>프로필 불러오는 중…</p>;
  }

  return (
    <div>
      <h2>내 프로필</h2>
      <p><strong>카카오 ID:</strong> {profile.kakao_id}</p>
      <p><strong>닉네임:</strong> {profile.nickname}</p>
      <img src={profile.profile_image} alt="프로필 이미지" width={80} />
      <p><em>가입 일자: {new Date(profile.created_at).toLocaleString()}</em></p>
    </div>
  );
}