'use client';

import { ExternalLink, Clock, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SearchResponse } from '@/types';
import { formatPrice, formatRating, copyToClipboard } from '@/lib/utils';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';

interface ProductResultsProps {
  results: SearchResponse;
  onNewSearch: () => void;
}

export function ProductResults({ results, onNewSearch }: ProductResultsProps) {
  const handleVisitLink = async (url: string) => {
    try {
      await copyToClipboard(url);
      toast.success('链接已复制到剪贴板，正在打开...');
      // 稍微延迟打开新窗口，让用户看到提示
      setTimeout(() => {
        window.open(url, '_blank', 'noopener,noreferrer');
      }, 500);
    } catch {
      // 如果复制失败，直接打开链接
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  const getRankBadgeColor = (rank: number) => {
    switch (rank) {
      case 1:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 2:
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case 3:
        return 'bg-orange-100 text-orange-800 border-orange-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return '🥇';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return `#${rank}`;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8"
    >
      {/* Results Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-4">
          <h2 className="text-3xl font-bold text-foreground">
            为您推荐的最佳商品
          </h2>
          <Badge variant="secondary" className="text-sm">
            共 {results.total_results} 个结果
          </Badge>
        </div>

        <div className="flex items-center justify-center space-x-6 text-sm text-muted-foreground">
          <div className="flex items-center space-x-1">
            <Clock className="h-4 w-4" />
            <span>用时 {results.search_time.toFixed(2)}s</span>
          </div>
          {results.cached && (
            <Badge variant="outline" className="text-xs">
              缓存结果
            </Badge>
          )}
        </div>

        <Button onClick={onNewSearch} variant="outline">
          搜索其他商品
        </Button>
      </div>

      {/* Product Cards */}
      <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-3">
        {results.products.map((product, index) => (
          <motion.div
            key={product.rank}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <Card className="h-full flex flex-col relative overflow-hidden hover:shadow-lg transition-shadow duration-300">
              {/* Rank Badge */}
              <div className="absolute top-4 right-4 z-10">
                <Badge className={`${getRankBadgeColor(product.rank)} font-bold px-3 py-1`}>
                  <span className="mr-1">{getRankIcon(product.rank)}</span>
                  Top {product.rank}
                </Badge>
              </div>

              <CardHeader className="pb-3">
                <CardTitle className="text-lg leading-tight pr-16">
                  {product.product_name}
                </CardTitle>
                <div className="flex items-center space-x-3 text-sm">
                  {product.rating && (
                    <div className="flex items-center space-x-1">
                      <TrendingUp className="h-4 w-4 text-green-600" />
                      <span className="font-medium">
                        {formatRating(product.rating)}
                      </span>
                    </div>
                  )}
                  {product.price && (
                    <span className="font-semibold text-primary">
                      {formatPrice(product.price)}
                    </span>
                  )}
                </div>
              </CardHeader>

              <CardContent className="flex-1 flex flex-col space-y-4">
                <CardDescription className="text-sm leading-relaxed flex-1">
                  {product.description}
                </CardDescription>

                {product.best_for && (
                  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                    <p className="text-xs font-medium text-blue-800 dark:text-blue-200 mb-1">
                      适合人群
                    </p>
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      {product.best_for}
                    </p>
                  </div>
                )}

                {(product.pros || product.cons) && (
                  <div className="space-y-2">
                    {product.pros && product.pros.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-green-700 dark:text-green-300 mb-1">
                          优点：
                        </p>
                        <ul className="text-xs text-green-600 dark:text-green-400 space-y-1">
                          {product.pros.slice(0, 2).map((pro, i) => (
                            <li key={i} className="flex items-start">
                              <span className="mr-1">•</span>
                              <span>{pro}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {product.cons && product.cons.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-red-700 dark:text-red-300 mb-1">
                          注意事项：
                        </p>
                        <ul className="text-xs text-red-600 dark:text-red-400 space-y-1">
                          {product.cons.slice(0, 2).map((con, i) => (
                            <li key={i} className="flex items-start">
                              <span className="mr-1">•</span>
                              <span>{con}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                <div className="pt-2">
                  <Button
                    onClick={() => handleVisitLink(product.source_link)}
                    className="w-full"
                    variant="default"
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    查看详情
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Footer */}
      <div className="text-center pt-8 border-t">
        <p className="text-sm text-muted-foreground mb-4">
          以上推荐基于实时网络搜索和AI分析，建议您在购买前进一步核实产品信息
        </p>
        <div className="flex justify-center space-x-4">
          <Button onClick={onNewSearch} variant="outline" size="sm">
            重新搜索
          </Button>
        </div>
      </div>
    </motion.div>
  );
}