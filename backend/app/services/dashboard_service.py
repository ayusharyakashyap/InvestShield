import pandas as pd
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import Counter
import os

class DashboardService:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(__file__), "../../data")
        self.flagged_content = []
    
    def get_flagged_content_from_db(self, db):
        """Fetch flagged content from the database"""
        from app.models import FlaggedContent
        from sqlalchemy.orm import Session
        import json
        
        if not db or not isinstance(db, Session):
            # If no DB session provided, return empty list
            return []
        
        # Query all flagged content from the database
        flagged_content_records = db.query(FlaggedContent).all()
        flagged_content = []
        
        for record in flagged_content_records:
            # Parse keywords_found JSON string
            try:
                keywords = json.loads(record.keywords_found) if record.keywords_found else []
            except:
                keywords = []
                
            flagged_content.append({
                'id': record.id,
                'content': record.content_text,
                'source': record.source,
                'fraud_type': record.fraud_type,
                'risk_score': record.risk_score,
                'confidence_score': record.confidence_score,
                'created_at': record.created_at,
                'keywords_found': keywords
            })
        
        return flagged_content
    
    def get_dashboard_stats(self, db=None) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics"""
        # Get flagged content from DB if available
        flagged_content = self.get_flagged_content_from_db(db) if db else self.flagged_content
        
        current_time = datetime.now()
        today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = current_time - timedelta(days=7)
        
        # Filter content by time periods
        today_content = [c for c in flagged_content if c['created_at'] >= today_start]
        week_content = [c for c in flagged_content if c['created_at'] >= week_start]
        
        # Calculate basic stats
        stats = {
            'total_flagged_content': len(flagged_content),
            'flagged_content_today': len(today_content),
            'flagged_content_week': len(week_content),
            'average_risk_score': round(sum(c['risk_score'] for c in flagged_content) / len(flagged_content), 1) if flagged_content else 0,
            'high_risk_content': len([c for c in flagged_content if c['risk_score'] > 80]),
            'medium_risk_content': len([c for c in flagged_content if 50 <= c['risk_score'] <= 80]),
            'low_risk_content': len([c for c in flagged_content if c['risk_score'] < 50])
        }
        
        # Top fraud types
        fraud_types = [c['fraud_type'] for c in flagged_content]
        fraud_type_counts = Counter(fraud_types)
        stats['top_fraud_types'] = [
            {'type': fraud_type, 'count': count}
            for fraud_type, count in fraud_type_counts.most_common(5)
        ]
        
        # Source distribution
        sources = [c['source'] for c in self.flagged_content]
        source_counts = Counter(sources)
        stats['source_distribution'] = [
            {'source': source, 'count': count}
            for source, count in source_counts.most_common()
        ]
        
        # Recent high-risk alerts
        high_risk_recent = sorted(
            [c for c in self.flagged_content if c['risk_score'] > 80],
            key=lambda x: x['created_at'],
            reverse=True
        )[:5]
        
        stats['recent_high_risk_alerts'] = [
            {
                'id': c['id'],
                'content_preview': c['content'][:100] + "..." if len(c['content']) > 100 else c['content'],
                'source': c['source'],
                'risk_score': c['risk_score'],
                'fraud_type': c['fraud_type'],
                'time_ago': self._time_ago(c['created_at'])
            }
            for c in high_risk_recent
        ]
        
        # Hourly distribution for today
        hourly_stats = self._get_hourly_distribution(today_content)
        stats['hourly_distribution'] = hourly_stats
        
        # Risk score distribution
        stats['risk_score_distribution'] = self._get_risk_score_distribution()
        
        return stats
    
    def get_trend_analysis(self, days: int = 7, db=None) -> Dict[str, Any]:
        """Get trend analysis for specified number of days"""
        # Get flagged content from DB if available
        flagged_content = self.get_flagged_content_from_db(db) if db else self.flagged_content
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Filter content within date range
        trend_content = [
            c for c in flagged_content
            if start_date <= c['created_at'] <= end_date
        ]
        
        # Daily trends
        daily_trends = {}
        for i in range(days):
            day = start_date + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_content = [
                c for c in trend_content
                if day_start <= c['created_at'] < day_end
            ]
            
            daily_trends[day.strftime('%Y-%m-%d')] = {
                'total_flagged': len(day_content),
                'high_risk': len([c for c in day_content if c['risk_score'] > 80]),
                'avg_risk_score': round(sum(c['risk_score'] for c in day_content) / len(day_content), 1) if day_content else 0
            }
        
        # Fraud type trends
        fraud_type_trends = {}
        for content in trend_content:
            fraud_type = content['fraud_type']
            date_key = content['created_at'].strftime('%Y-%m-%d')
            
            if fraud_type not in fraud_type_trends:
                fraud_type_trends[fraud_type] = {}
            
            if date_key not in fraud_type_trends[fraud_type]:
                fraud_type_trends[fraud_type][date_key] = 0
            
            fraud_type_trends[fraud_type][date_key] += 1
        
        return {
            'daily_trends': daily_trends,
            'fraud_type_trends': fraud_type_trends,
            'period': f'{days} days',
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'total_analyzed': len(trend_content)
        }
    
    def get_flagged_content(self, limit: int = 50, fraud_type: str = None, 
                           min_risk_score: float = None, db=None) -> Dict[str, Any]:
        """Get flagged content with filtering options"""
        # Get flagged content from DB if available
        flagged_content = self.get_flagged_content_from_db(db) if db else self.flagged_content
        filtered_content = flagged_content.copy()
        
        # Apply filters
        if fraud_type:
            filtered_content = [c for c in filtered_content if c['fraud_type'] == fraud_type]
        
        if min_risk_score is not None:
            filtered_content = [c for c in filtered_content if c['risk_score'] >= min_risk_score]
        
        # Sort by creation time (newest first)
        filtered_content.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Apply limit
        limited_content = filtered_content[:limit]
        
        # Format for response
        formatted_content = []
        for content in limited_content:
            formatted_content.append({
                'id': content['id'],
                'content_text': content['content'],
                'source': content['source'],
                'fraud_type': content['fraud_type'],
                'risk_score': content['risk_score'],
                'confidence_score': content['confidence_score'],
                'keywords_found': content['keywords_found'],
                'created_at': content['created_at'].isoformat(),
                'time_ago': self._time_ago(content['created_at'])
            })
        
        return {
            'flagged_content': formatted_content,
            'total_found': len(filtered_content),
            'showing': len(limited_content),
            'filters_applied': {
                'fraud_type': fraud_type,
                'min_risk_score': min_risk_score,
                'limit': limit
            }
        }
    
    def add_flagged_content(self, content_data: Dict[str, Any], db=None) -> Dict[str, Any]:
        """Add new flagged content to the database"""
        try:
            if db:
                # Save to database
                from app.models import FlaggedContent
                import json
                
                new_content = FlaggedContent(
                    content_text=content_data['content'],
                    source=content_data.get('source', 'manual'),
                    fraud_type=content_data['fraud_type'],
                    risk_score=content_data['risk_score'],
                    confidence_score=content_data['confidence_score'],
                    keywords_found=json.dumps(content_data.get('keywords_found', [])),
                    is_verified_fraud=False,
                    reported_by=content_data.get('reported_by', 'system')
                )
                
                db.add(new_content)
                db.commit()
                db.refresh(new_content)
                
                return {
                    'success': True,
                    'content_id': new_content.id,
                    'message': 'Content flagged and saved to database successfully'
                }
            else:
                # Fallback to in-memory storage for backward compatibility
                new_id = max([c['id'] for c in self.flagged_content], default=0) + 1
                
                new_content = {
                    'id': new_id,
                    'content': content_data['content'],
                    'source': content_data.get('source', 'manual'),
                    'fraud_type': content_data['fraud_type'],
                    'risk_score': content_data['risk_score'],
                    'confidence_score': content_data['confidence_score'],
                    'keywords_found': content_data.get('keywords_found', []),
                    'created_at': datetime.now()
                }
                
                self.flagged_content.append(new_content)
                
                return {
                    'success': True,
                    'content_id': new_id,
                    'message': 'Content flagged successfully'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to save flagged content'
            }
    
    def _get_hourly_distribution(self, content_list: List[Dict]) -> List[Dict[str, Any]]:
        """Get hourly distribution of flagged content"""
        hourly_counts = {i: 0 for i in range(24)}
        
        for content in content_list:
            hour = content['created_at'].hour
            hourly_counts[hour] += 1
        
        return [
            {'hour': hour, 'count': count}
            for hour, count in hourly_counts.items()
        ]
    
    def _get_risk_score_distribution(self) -> List[Dict[str, Any]]:
        """Get risk score distribution"""
        ranges = [
            (0, 25, 'Low'),
            (25, 50, 'Low-Medium'),
            (50, 75, 'Medium-High'),
            (75, 90, 'High'),
            (90, 100, 'Very High')
        ]
        
        distribution = []
        for min_score, max_score, label in ranges:
            count = len([
                c for c in self.flagged_content
                if min_score <= c['risk_score'] < max_score
            ])
            distribution.append({
                'range': f'{min_score}-{max_score}',
                'label': label,
                'count': count
            })
        
        return distribution
    
    def _time_ago(self, past_time: datetime) -> str:
        """Calculate human-readable time difference"""
        now = datetime.now()
        diff = now - past_time
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    def get_export_data(self, format_type: str = 'json') -> Dict[str, Any]:
        """Export flagged content data"""
        export_data = []
        for content in self.flagged_content:
            export_item = {
                'id': content['id'],
                'content': content['content'],
                'source': content['source'],
                'fraud_type': content['fraud_type'],
                'risk_score': content['risk_score'],
                'confidence_score': content['confidence_score'],
                'keywords_found': ', '.join(content['keywords_found']),
                'created_at': content['created_at'].isoformat()
            }
            export_data.append(export_item)
        
        return {
            'data': export_data,
            'format': format_type,
            'exported_at': datetime.now().isoformat(),
            'total_records': len(export_data)
        }
