'use client';

import { useState } from 'react';
import { Search } from 'lucide-react';
import { SearchForm } from '@/components/search/search-form';
import { ProductResults } from '@/components/search/product-results';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { SearchResponse } from '@/types';

export default function HomePage() {
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (results: SearchResponse) => {
    setSearchResults(results);
    setHasSearched(true);
  };

  const handleLoadingChange = (loading: boolean) => {
    setIsLoading(loading);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm dark:bg-gray-900/80">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <Search className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">
                  Top3-Hunter
                </h1>
                <p className="text-sm text-muted-foreground">
                  智能商品推荐引擎
                </p>
              </div>
            </div>
            <nav className="flex items-center space-x-6">
              <a
                href="/admin"
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                管理后台
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Hero Section */}
          {!hasSearched && !isLoading && (
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold tracking-tight text-foreground mb-4">
                找到最适合您的
                <span className="text-primary"> Top 3 </span>
                商品推荐
              </h2>
              <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
                基于实时网络搜索和AI分析技术，我们从全网为您筛选出最优质的商品推荐
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                <div className="text-center p-6 rounded-lg bg-card border">
                  <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                    <Search className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="font-semibold mb-2">实时搜索</h3>
                  <p className="text-sm text-muted-foreground">
                    整合全网最新商品信息，确保推荐时效性
                  </p>
                </div>
                <div className="text-center p-6 rounded-lg bg-card border">
                  <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                    <div className="h-6 w-6 text-primary font-bold">AI</div>
                  </div>
                  <h3 className="font-semibold mb-2">智能分析</h3>
                  <p className="text-sm text-muted-foreground">
                    大语言模型深度分析，提供专业购买建议
                  </p>
                </div>
                <div className="text-center p-6 rounded-lg bg-card border">
                  <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                    <div className="h-6 w-6 text-primary">⭐</div>
                  </div>
                  <h3 className="font-semibold mb-2">精选推荐</h3>
                  <p className="text-sm text-muted-foreground">
                    从海量商品中精选Top 3，节省您的选择时间
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Search Form */}
          <div className={hasSearched ? "mb-8" : "mb-16"}>
            <SearchForm
              onSearch={handleSearch}
              onLoadingChange={handleLoadingChange}
            />
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="text-center py-16">
              <LoadingSpinner size="lg" className="mx-auto mb-4" />
              <p className="text-lg font-medium text-foreground mb-2">
                正在为您搜索最佳商品...
              </p>
              <p className="text-sm text-muted-foreground">
                这可能需要几秒钟时间
              </p>
            </div>
          )}

          {/* Search Results */}
          {!isLoading && searchResults && (
            <ProductResults
              results={searchResults}
              onNewSearch={() => {
                setHasSearched(false);
                setSearchResults(null);
              }}
            />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/80 backdrop-blur-sm dark:bg-gray-900/80 mt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-sm text-muted-foreground">
            <p>
              © 2024 Top3-Hunter. 基于AI技术的智能商品推荐引擎
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}