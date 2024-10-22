from django.contrib.auth.mixins import LoginRequiredMixin, \
    UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404, HttpRequest, HttpResponse, \
    HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView


from .models import Post, Category, Comment
from .forms import CommentForm

POSTS_SLICE = 5


class RedirectToProfileMixin:
    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class CommentFormMixin:
    model = Comment
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('blog:post_detail',
                                            args=[self.kwargs['post_id']]))


class EditProfileView(LoginRequiredMixin, RedirectToProfileMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'blog/edit_profile.html'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])


class PostCreateView(LoginRequiredMixin, RedirectToProfileMixin, CreateView):
    model = Post
    fields = ['title', 'text', 'category', 'location', 'image', 'pub_date']
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostEditView(LoginRequiredMixin, UserPassesTestMixin,
                   RedirectToProfileMixin, UpdateView):
    model = Post
    fields = ['title', 'text', 'category', 'location', 'image', 'pub_date']
    template_name = 'blog/create.html'
    pk_url_kwarg = 'id'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse_lazy(
            'blog:post_detail',
            kwargs={'id': self.get_object().id}
        )
        )


class CommentCreateView(LoginRequiredMixin, CommentFormMixin, CreateView):
    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin,
                        CommentFormMixin, DeleteView):
    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user


class CommentEditView(LoginRequiredMixin, UserPassesTestMixin,
                      CommentFormMixin, UpdateView):
    form_class = CommentForm

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin,
                     RedirectToProfileMixin, DeleteView):
    model = Post

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


def get_filtered_posts(user=None, category=None):
    now = timezone.now()
    filters = {
        'is_published': True,
        'category__is_published': True,
        'pub_date__lte': now,
    }

    if user:
        filters['author'] = user

    if category:
        filters['category'] = category

    return Post.objects.filter(**filters).\
        select_related('category', 'author').\
        annotate(comment_count=Count('comments')).order_by('-pub_date')


def index(request: HttpRequest) -> HttpResponse:
    post_list = get_filtered_posts()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    return render(request, 'blog/index.html', context)


def post_detail(request: HttpRequest, id: int) -> HttpResponse:
    post = get_object_or_404(Post.objects.select_related('category', 'author'),
                             pk=id)

    if (
        (not post.category.is_published or not post.is_published
            or post.pub_date > timezone.now())
        and post.author != request.user
    ):
        raise Http404("Пост не найден.")

    comments = Comment.objects.filter(post=post).\
        select_related('author').order_by('created_at')
    form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request: HttpRequest, category_slug: str) -> HttpResponse:
    category = get_object_or_404(Category, slug=category_slug,
                                 is_published=True)
    posts = get_filtered_posts(category=category)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


class ProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        posts = Post.objects.filter(author=user).\
            annotate(comment_count=Count('comments')).order_by('-pub_date')
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context
