'use client';

import { useState } from 'react';
import { Search as SearchIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { SearchRequest, SearchResponse } from '@/types';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

interface SearchFormProps {
  onSearch: (results: SearchResponse) => void;
  onLoadingChange: (loading: boolean) => void;
}

export function SearchForm({ onSearch, onLoadingChange }: SearchFormProps) {
  const [keyword, setKeyword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!keyword.trim()) {
      toast.error('请输入商品关键词');
      return;
    }

    setIsSubmitting(true);
    onLoadingChange(true);

    try {
      const request: SearchRequest = { keyword: keyword.trim() };
      const results = await api.getTopProducts(request);

      onSearch(results);

      if (results.cached) {
        toast.success('已从缓存中获取推荐结果');
      } else {
        toast.success('为您找到了最新的推荐商品！');
      }
    } catch (error) {
      console.error('Search error:', error);
      toast.error(error instanceof Error ? error.message : '搜索失败，请稍后重试');
    } finally {
      setIsSubmitting(false);
      onLoadingChange(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setKeyword(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit(e as any);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="relative">
        <div className="flex items-center space-x-2">
          <div className="relative flex-1">
            <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="输入商品关键词，例如：无线耳机、智能手机、咖啡机..."
              value={keyword}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              className="pl-10 pr-4 py-3 text-base h-12"
              disabled={isSubmitting}
              autoComplete="off"
              autoFocus
            />
          </div>
          <Button
            type="submit"
            disabled={isSubmitting || !keyword.trim()}
            className="h-12 px-6"
          >
            {isSubmitting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                搜索中...
              </>
            ) : (
              <>
                <SearchIcon className="h-4 w-4 mr-2" />
                搜索推荐
              </>
            )}
          </Button>
        </div>

        {/* 搜索建议 */}
        <div className="mt-3 flex flex-wrap gap-2">
          <span className="text-sm text-muted-foreground">热门搜索：</span>
          {['无线耳机', '智能手机', '笔记本电脑', '咖啡机', '运动鞋'].map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => setKeyword(suggestion)}
              className="text-sm text-muted-foreground hover:text-primary transition-colors underline-offset-4 hover:underline"
              disabled={isSubmitting}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </form>
  );
}