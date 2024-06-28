from django.urls import path 


from blog.views import (
	BlogPageView, 
	SearchResultsListView, 
	PostDetailView,
	ContactView,
	Suscribir,
	FAQView,
	CategoryPageView,
)


app_name = 'blog'
urlpatterns = [

 	path('blog/', BlogPageView.as_view(), name='blog'),
 	path('blog/<slug:slug>', PostDetailView.as_view(), name='blog_detail'),
 	path('search/', SearchResultsListView.as_view(), name='search_results'),
 	path('contact/', ContactView.as_view(), name='contact'),
	path('category/<int:pk>', CategoryPageView.as_view(), name='category'),
 	path('suscribirse/',Suscribir.as_view(), name='suscribirse'),
 	path('FAQ/',FAQView.as_view(), name='FAQ'),

]