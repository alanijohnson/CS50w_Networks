var auth_user;
var auth_username;
let counter = 0;
let quantity = 5;

document.addEventListener('DOMContentLoaded', async function() {
    
    // Save currect user and users
    auth_user = JSON.parse(document.getElementById('user_id').textContent);
    var users = JSON.parse(document.getElementById('users').textContent);
    
    // Add Listeners for Links
    document.querySelector('#all_posts_link').addEventListener('click', () => {
        document.querySelector('#header-title').innerHTML = `All Posts`
        load_all_posts()});
    if (auth_user != null){
        auth_username = users[auth_user].username;
        document.querySelector('#following_link').addEventListener('click', () => load_following(auth_username));
    }
    
    new_post_button = document.querySelector('#new_post');
    if (new_post_button != null){
        new_post_button.addEventListener('click', (event) => {
            document.querySelector("#post_entry_div").style.margin = "0px";
            document.querySelector("#modal-title").innerHTML = "";
            
            // add listener to post submit to submit a new post. When clicking the post link.
            post_submit = document.querySelector('#submit_post')
            post_submit.disabled = true;
            document.querySelector('#submit_post').onclick = async function new_post_submit(event) {
                var result = await submit(document.querySelector('#content_field').value);
                console.log(result);
                submit_post_view_updates(result);
                
                document.querySelector('#submit_post').removeEventListener('click', new_post_submit);
                event.stopPropagation();
            };
            
            
            new_post_click();
        });
    }
    
    
    
    content_field = document.querySelector('#content_field');
    document.querySelector('#content_field').onkeyup = () => {
        activate_submit();
    }
    
    // Load posts based on logged in or not
    if(auth_user){
        console.log('show following');
        load_following(auth_username);
    } else {
        console.log('DOM content load posts');
        load_all_posts();
    }
    
});

async function submit_post_view_updates(result){
    console.log(result);
    if (!result.error){
        $('#modal_createPost').modal('hide');
        var post = await get_post(result.id);
        console.log(post);
        update_post_stats(post, document.querySelector(`#post_div_${post.id}`), reload=false);
        
        // update root as well
        if (post.root.id){
            update_post_stats(post.root, document.querySelector(`#post_div_${post.root.id}`), reload=true);
        }
        
    }
}


async function is_user_following(user_id, id){
    // Determine if the user (user_id) is already following the user with id=id
    var persons = await get_users();
    return user_id != null ? persons[user_id].following.includes(id) : null;
}

async function does_user_like(post_id){
    // Determine if the user (user_id) already likes the post with id=post_id
    var post = await get_post(post_id);
    //console.log(`does user like func: ${post_id}`)
    //console.log(post)
    //console.log(`${auth_user} likes: ${post.likes.includes(auth_user)}`)

    return post != null ? post.likes.includes(auth_user) : null;
}

async function can_reshare(post_id){
    // A user cannot retweet the same post that is already retweeted with 0 content.
    
    var post = await get_post(post_id);
    //console.log(post)
    
    if (post == null){
        return [null,null]
    }
    
    // see if the post_id is in the children of the current item (i.e. the post was
    var children = post.children
    // console.log(children)
    // console.log(children != null)
    if(children != null){
        // if post has been plain retweeted with no comment. Cannot reshare again
        for (var [child_id,data] of Object.entries(children)){
            //console.log(id)
            //console.log(data)
            if (data.root_type == 2 && data.user == auth_user){
                //console.log(`${post_id}: found the child retweet ${child_id}`)
                return [data.content != "", child_id]
            }
        }
        
    }

    // see if the post is the retweet
    //console.log(post.root.id)
    //console.log(post.root.children)
    
    if (post.root.id != null && post.root.children != null && post.root.children[post_id] != null ) {
        //console.log(`${post.id} found the root ${post.root.id}`)
        return [post.root.children[post_id].content != "", post_id]
    }
    
    // console.log(`${post_id}: return true - can reshare`)
    return [true,null]
}

async function follow_click(id){
   
    is_following = await is_user_following(auth_user,id);
    if(is_following){
        // user is following user
        error = await follow("unfollow",id)
    } else {
        // user is not following
        error = await follow("follow",id)
    }
    
}

async function like_click(post_id){
    
    console.log('like clicked')
    does_like = await does_user_like(post_id);
    if(does_like){
        // user likes post
        console.log(`unliking ${post_id}`)
        error = await like("unlike",post_id)
    } else {
        // user is not following
        console.log(`liking ${post_id}`)
        error = await like("like",post_id)
    }
    
    console.log('like click finished')
    
}

async function reshare_click(post_id){
    
    console.log('reshare clicked')
    var crs = await can_reshare(post_id);
    if(crs[0]){
        // user can click reshare
        console.log(`resharing ${post_id}`)
        error = await submit("",id=null,alert=null, root=post_id,root_type=2,div=null)
        await update_reshare_button(post_id)
    } else {
        // user can't reshare, so has unshare option.
        await unshare_click(crs[1], post_id);
    }
    
    return
    
}

async function unshare_click(post_to_delete, post_id){
    
    console.log(`deleting ${post_to_delete}`)
    post_div = document.querySelector(`#post_div_${post_to_delete}`)
    var post_delete = await get_post(post_to_delete);
    console.log(`parent ${post_to_delete}: ${post.root.id}`)
    await delete_post(post_to_delete)
    
    // if post div is on the page animate delete
    if(post_div){
        post_div.classList.toggle('collapsed');
        
    }
    
    // update butttons
    // deleted self need to update parent
    post_id = post_delete.root.id
    
    
    post = await get_post(post_id)
    await update_reshare_button(post_id)
    await update_post_stats(post, document.querySelector(`#post_div_${post.id}`), reload=false);
    
}

async function update_reshare_button(post_id){
    var b = await can_reshare(post_id);
    console.log(b)
    var button = document.querySelector(`#reshare-${post_id}`);
    console.log(button)
    if (button != null){
        button.innerHTML = b[0] ? "reshare" : "unshare";
    }
}

async function update_post_stats(post, div, reload=true){
    //console.log('update stats');
    if (div == null || post == null){
        return;
    }
    
    if(reload){
        post = await get_post(post.id);
    }
    
    if(post == null){
        return;
    }
    
//    console.log(post)
//    console.log(div.querySelector(`#comment-count-${post.id}`));
//    console.log(div.querySelector(`#like-count-${post.id}`));
//    console.log(div.querySelector(`#reshare-count-${post.id}`));
    div.querySelector(`#comment-count-${post.id}`).innerHTML = post.stats.comments;
    div.querySelector(`#like-count-${post.id}`).innerHTML = post.stats.likes;
    div.querySelector(`#reshare-count-${post.id}`).innerHTML = post.stats.reshares;
    
}

// query for an entire set of posts (user page, following page, and all)
async function load_posts(id=null,following_only=false,start=counter,num=quantity){
    //console.log(`\nid:${id}\nfollowing_only:${following_only}`);
    // save view items
    div = document.querySelector('#feed');
        
    user_header = document.querySelector('#user-header');
    user_header.style.display = "none";
    
    // set view
    document.querySelector('#create_post_form').style.display = "None";
    
    // users
    users = await get_users();
    //console.log(id);
    
    // set up user header for user profile
    url = '/posts?';
    
    
    if(following_only){
        
        url = '/following?';
        
    } else if (id != null){
        // append to url to access user profile page
        url += `user=${id}`;
        
        // set up user header
        user_header.innerHTML = `<div class="d-flex justify-content-around" style="margin-bottom:20px; "><div><div id="followers_count" style="text-align: center;">${users[id].followers.length}</div><div> followers</div></div><div><div id="following_count" style="text-align: center;">${users[id].following.length}</div><div>following</div></div><div class="d-flex align-items-center"><button id="follow-${id}" class="btn btn-secondary">UnLabled</button></div>`;
        user_header.style.display = "block";
        
        // set up follow button
        follow_button = document.querySelector(`#follow-${id}`);
        follow_button.innerHTML = await is_user_following(auth_user,id) ? "unfollow" : "follow";
        
        // hide user id button if on your own page.
        if( auth_user == null || auth_user == id ){
            follow_button.style.visibility = "hidden";
        } else {
            follow_button.addEventListener('click', () => {
                follow_click(id);
            })
        }
        
    }
    
    // limit the loading for the home page
    if(counter != null){
        url += `&start=${start}&count=${num}`;
    }
    
    console.log(url);
    
    const response = await fetch(url);
    const result = await response.json();
    
    if (result.length == 0){
        no_posts = document.createElement('div');
        no_posts.style.margins = "50px";
        no_posts.className = 'd-flex justify-content-center align-items-center';
        no_posts.innerHTML = "No Posts to show"
        div.append(no_posts);
    }
    
    for (post of result) {
        
        // load the post for the root if its a retweet.
        // update status field to make it show it is a retweet from the current post.
       
        await load_post_view(post,div);
        
        
        
    }
    

}

// load the indivual post items
async function load_post_view(post,div,prepend=false){
    // show is the post information that should be shown.
    // it is not necessarily the post and may be the root if the post was reshared.
    
    var show;
    if(post.root_type == 2){
        show = await get_post(post.root.id);
    } else {
        show = post;
    }
    
    
    // 1. create post div
    post_div = document.createElement('div');
    post_div.className = 'post'
    post_div.setAttribute('id',`post_div_${post.id}`);
    
    
    
    // 1.1 create status div
    status_div = document.createElement('div')
    status_div.setAttribute('id',`status_div_${post.id}`)
    status_div.style.display = "none"
    status_div.className = 'media flex-column status';
    status_div.innerHTML = `@${post.username} reshared this post.`
    status_div.style.paddingBottom = "10px";
    
                            
    // 1.2 Create content Div. Set to media with Black text
    content_div = document.createElement('div');
    content_div.className = 'media';
    content_div.style.color = "Black";
    content_div.setAttribute("id",`content_div_${post.id}`)
                            
    // 1.2.1 Create Image Div for user profile picture
    image = document.createElement('img');
    image.className = "mr-3 align-self-start link_to_profile"
    image.src = show.picture;
    image.style.borderRadius = "50%";
    image.style.width = "50px";
    image.style.height = "50px";
    image.style.objectFit = "cover";
    
    // 1.2.2 create right div to display the rest of the content
    
    // icons credited to https://www.glyphicons.com/
    right_div = document.createElement('div');
    right_div.className = "media-body";
    right_div.innerHTML = `<div id="profile_name_${post.id}" class="d-flex w-100 justify-content-between"><div class="link_to_profile"><strong>${show.name}</strong> @${show.username}</div> ${show.date_posted}</div><p id="post_text_${post.id}">${show.content}</p><div id="edit_form_${post.id}"></div><div id="post_actions_${post.id}" class="d-flex d-flex align-items-center justify-content-around" ><div><div class="d-flex justify-content-center" id="comment-count-${post.id}">#</div><button id="comment-${post.id}" class="post-action-button btn btn-primary">comment</button></div><div><div class="d-flex justify-content-center" id="reshare-count-${post.id}">#</div><button id="reshare-${post.id}" class="post-action-button btn btn-success">reshare</button></div><div><div class="d-flex justify-content-center" id="like-count-${post.id}">#</div><button id="like-${post.id}" class="post-action-button like-button btn btn-danger">like</button></div><div class="d-flex flex-wrap justify-content-center align-self-end"><button id="edit-${post.id}" class="post-action-button btn btn-secondary">edit</button><button id="delete-${post.id}" class="post-action-button btn btn-dark">delete</button></div></div>`;
    right_div.style.marginBottom = "10px";
    
    right_div.querySelectorAll('.post-action-button').forEach(button => {
            button.style.marginLeft = "1px";
            button.style.marginLeft = "1px";
    });
    
    update_post_stats(post, right_div, false);
    
    if(post.root_type == 2){
        // update all of the content to show the root retweet with a message
        status_div.style.display = "block";
        
    } else if (post.root_type == 1){
        status_div.style.display = "block";
        status_div.innerHTML = `@${post.username} commented on @${post.root.username}'s post`;
    }
    
    // append both divs to post div. Then append post div to the feed.
    content_div.append(image);
    content_div.append(right_div);
    post_div.style.borderTop = "thin solid gray";
    post_div.append(status_div);
    post_div.append(content_div);
    
    
    // add listener for removing div based on transition end
    post_div.addEventListener("transitionend", async (event) =>  {
        if(event.propertyName == "max-height") {
            console.log('transition end');
            document.querySelector(`#post_div_${post.id}`).remove();
        }
    })
    
    // add post to the feed
    if(prepend){
        div.prepend(post_div);
    } else {
        div.append(post_div);
    }
    counter++;
    
    
    // set the username & image divs to link to user profile
    content_div.querySelectorAll('.link_to_profile').forEach(div =>{
        div.style.cursor = "pointer";
        div.onclick = () => {
            load_profile(show.user,show.username);
            event.stopPropagation();
        }
    })
    
    // set the content div to link to post page
    content_div.onclick = () => {
            load_post_page(show.id);
            //event.stopPropagation();
    }
    
    // set the status div to link to the users page
    status_div.onclick = () => {
        if (post.root_type == 2){
            load_profile(post.user,post.username);
        } else if (post.root_type == 1){
            load_post_page(post.root.id);;
        }

        event.stopPropagation();
    }
    
    // Hide actions for not logged in user or define button actions
    if(auth_user == null){
        document.querySelector(`#delete-${post.id}`).style.visibility = "hidden";
        document.querySelectorAll(".post-action-button").forEach(button => {
            button.style.disabled = "true";
            button.style.background = "#d2d5d9";
            button.onclick = (e) => {
                // fix this
                e.stopPropagation();
            };
        })
    } else {
        
        // comment button
        comment_button = document.querySelector(`#comment-${post.id}`);
        comment_button.setAttribute("href","#modal_createPost");
        comment_button.setAttribute("data-toggle","modal");
        document.querySelector(`#comment-${post.id}`).addEventListener('click', async (event) => {
            event.stopPropagation();
            var post_div = document.querySelector(`#post_div_${post.id}`).cloneNode(true);
            //console.log(post_div);
            post_div.querySelector(`#post_actions_${post.id}`).remove();
            post_div.style.borderTop = "";
            post_div.style.borderBottom = "thin solid gray";
            post_div.style.padding = "";
            post_div.style.marginBottom = "10px";
            
            post_comment(post.id,post_div);
            
            
            
        })
        
        // reshare button
        reshare_button = document.querySelector(`#reshare-${post.id}`);
        crs = await can_reshare(post.id);
//                    console.log(b)
//                    console.log(`${post.id} can reshare: ${b[0]}`);
        document.querySelector(`#reshare-${post.id}`).innerHTML = crs[0] ? "reshare" : "unshare";
        document.querySelector(`#reshare-${post.id}`).addEventListener('click', async (event) => {
            event.stopPropagation();
            await reshare_click(post.id)
//                        var button = document.querySelector(`#reshare-${post.id}`);
//                        if (button != null){
//                            b = await can_reshare(post.id)[0];
//                            console.log(`${post.id} can reshare: ${b}`);
//                            button.innerHTML = b ? "reshare" : "unshare";
//                        }
            update_post_stats(post, document.querySelector(`#post_div_${post.id}`), reload=true)
            
        })
        
        
        // like button
        like_button = document.querySelector(`#like-${post.id}`);
        document.querySelector(`#like-${post.id}`).innerHTML = await does_user_like(post.id) ? "unlike" : "like";
        document.querySelector(`#like-${post.id}`).addEventListener('click', async (event) => {
            event.stopPropagation();
            await like_click(post_id=post.id);
            await update_post_stats(post, document.querySelector(`#post_div_${post.id}`), reload=true)
            
        });
        
        
        // delete button
        if ( auth_user == post.user){
            document.querySelector(`#delete-${post.id}`).style.visibility = "visible";
            document.querySelector(`#delete-${post.id}`).style.marginLeft = "0.5px";
            document.querySelector(`#delete-${post.id}`).addEventListener('click', async () => {
                event.stopPropagation();
                console.log('delete clicked')
                post_div = document.querySelector(`#post_div_${post.id}`)
                await delete_post(post.id)
                post_div.classList.toggle('collapsed');
                update_reshare_button(post.root.id)
                update_post_stats(post, document.querySelector(`#post_div_${post.root.id}`), reload=true)
                

            })
        } else {
            document.querySelector(`#delete-${post.id}`).style.visibility = "hidden";
        }
        
    }
    
    
    
    // Create edit form
    edit_form = document.createElement('form');
    edit_form.setAttribute("method","post");
    edit_form.innerHTML = `<div class="d-flex w-100 justify-content-end"><div id="edit_alert_${post.id}" class="alert alert-danger" role="alert" style="display:none">Alert!</div><button class="btn btn-secondary" id="edit_close_${post.id}" type="button">Close</button></div><textarea style="width:100%; margin-bottom:10px;" id="edit_text_${post.id}" rows="3">${post.content}</textarea>`
    document.querySelector(`#edit_form_${post.id}`).append(edit_form);
    document.querySelector(`#edit_form_${post.id}`).style.display = "None";
    
    // edit button actions
    edit_button = document.querySelector(`#edit-${post.id}`);
    edit_button.style.marginRight = "0.5px";
    edit_button.setAttribute("data","edit");
    close_button = document.querySelector(`#edit_close_${post.id}`);
    if( auth_user == post.user && post.root_type != 2){
        
        // prevent event propagation when clicking edit field
        document.querySelector(`#edit_form_${post.id}`).onclick = (event) => {
            event.stopPropagation();
        }
        
        
        // set on click for close button
        close_button.onclick = (event) => {
            // revert back to edit state
            edit_button = document.querySelector(`#edit-${post.id}`);
            edit_button.innerHTML = "Edit";
            edit_button.setAttribute("data","edit");
            
            // show post text
            post_text = document.querySelector(`#post_text_${post.id}`)
            post_text.style.display = "block";
            
            // hide edit form and reset text
            document.querySelector(`#edit_form_${post.id}`).style.display = "none";
            document.querySelector(`#edit_text_${post.id}`).value = post.content;
            
            event.stopPropagation();
        }
        
        // set on click for edit/save button
        edit_button.style.visibility = "visible";
        edit_button.onclick = async (event) => {
            event.stopPropagation();
            var edit_button = document.querySelector(`#edit-${post.id}`);
            
            if(edit_button.getAttribute("data") == "edit"){
                // Edit state - hide post text, alert, and show form
                document.querySelector(`#post_text_${post.id}`).style.display = "None";
                document.querySelector(`#edit_alert_${post.id}`).style.display = "None";
                document.querySelector(`#edit_form_${post.id}`).style.display = "block";
                
                // update button text and button to save
                edit_button.innerHTML = "Save";
                edit_button.setAttribute("data","save");
            } else if (edit_button.getAttribute("data") == "save"){
                // Save Content
                var edit_text = document.querySelector(`#edit_text_${post.id}`);
                var content = edit_text.value;
                
                // get alert
                var alert = document.querySelector(`#edit_alert_${post.id}`);
                
                var result = await submit(content,id=post.id,alert=alert);
                var error = result.error;
                
                // if there is no error, set back to edit state
                if( !error ){
                    document.querySelector(`#post_text_${post.id}`).innerHTML = content;
                    document.querySelector(`#post_text_${post.id}`).style.display = "block";
                    document.querySelector(`#edit_form_${post.id}`).style.display = "none";
                    edit_button.innerHTML = "Edit";
                    edit_button.setAttribute("data","edit");
                    
                } else {
                    
                }
                
                
                
            }
            //event.stopPropagation();
            
        }
    } else {
        edit_button.style.visibility = "hidden";
    }

}

// load the post page
async function load_post_page(id){
    
    div = document.querySelector('#feed');
    div.innerHTML = "";
    document.querySelector('#show-more-posts').style.display = "none";
    
    result = await get_post(id);
    
    if (result != null){
    
        var username = result.username;
        var children = result.children_ids;
        var root_id = result.root.id;
        
        document.querySelector('#header-title').innerHTML = `@${username}'s Comment`
        
        load_post_view(result,div);
        
        // update status bar to say go to root if there is a root post
        if(root_id != null){
            document.querySelector(`#status_div_${result.id}`).innerHTML = `Go to root post by ${result.root.username}`
            document.querySelector(`#status_div_${result.id}`).onclick = () => {
                load_post_page(root_id);
            }
            document.querySelector(`#status_div_${result.id}`).style.display = 'block';
        }
        
        children_div = document.createElement('div');
        children_div.setAttribute('id','profile-children');
        children_div.style.marginLeft = "66px";
        div.append(children_div);
        
        // NEXT TODO:
        // could implement a load more children feature here as well instead of below.
        // Need to add another view to return a subset of children ids.
        // for the sake of not adding features forever, stopping here :)
        
        console.log(children)
        for (var i in children){
            console.log(children[i]);
            post = await get_post(children[i]);
            console.log(post);
            if (post != null){
                load_post_view(post, children_div)
            }
            
        
        }
        
    } else {
        
        div.innerHTML = "ERROR LOADING POST";
        
    }
    
}

// nesting for comments. Go one deep - https://getbootstrap.com/docs/4.0/layout/media-object/#nesting

// Functions to create and submit new post, comment, and retweet
function new_post_click(){
    document.querySelector('#modal-body-contents').innerHTML = "";
    new_post();
    //history.pushState({}, "", `newpost`);
}

function new_post(content=""){
    console.log("new_post");
    // set view
    document.querySelector('#content_field').value = content;
    document.querySelector('#create_post_form').style.display = "Block";
    alert = document.querySelector('#compose-alert');
    alert.style.display = "None";
    //document.querySelector('#exampleModalCenter').modal('show');
    //document.querySelector('#modal_createPost').showModal();
    image = document.querySelector('.profilepic');
    image.style.borderRadius = "50%";
    image.style.width = "50px";
    image.style.height = "50px";
    image.style.objectFit = "cover";
    $("#modal_createPost").modal('show');
}

// Function to submit post.
async function submit(content,id=null,alert=null, root=null,root_type=null,div=null) {
    //console.log(`submit ${id}`)
    
    error = null;
    var submission;
    // get alert element
    if (alert == null){
      alert = document.querySelector('#compose-alert');
      alert.style.display = "None";
    }
    
    
    const csrftoken = getCookie('csrftoken');
    // Create post object
    var post = {
        content: content,
        id: id,
        root: root,
        root_type: root_type,

    };
    
      
    // Post the email to send and load the sent mailbox.
    const response = await fetch('/submit/post',{
    //credentials: 'include',
    method: "POST",
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8',
        'X-CSRFToken': csrftoken
    },
    body: JSON.stringify(post)
    });
    
    const result = await response.json();

    if (result.error){
        console.log(result.error);
        error = result.error;
        alert.innerHTML = result.error; // update banner messaging
        alert.style.display = "Block"; // show banner
    } else {
        console.log(result.message);
        //$('#modal_createPost').modal('hide');
        // remove div
        if (div != null){
            div.remove();
        }
    }
    
    return result;
      
}
    
// function to reply to an existing comment.
function post_comment(root_id,div){
    console.log("post_comment");
    document.querySelector("#modal-title").innerHTML = "Comment";
    document.querySelector("#post_entry_div").style.marginLeft = "30px";
    post_submit = document.querySelector('#submit_post')
    post_submit.disabled = true;
    document.querySelector('#submit_post').onclick =  async function comment_submit() {
        //$('#modal_createPost').modal('hide');
        var result = await submit(document.querySelector('#content_field').value,undefined,undefined, root_id,1,div);
        await submit_post_view_updates(result);
        // do I need to remove this listener? yes
        document.querySelector('#submit_post').removeEventListener('click', comment_submit);
        //update_post_stats(post.root, document.querySelector(`#post_div_${post.root.id}`), reload=true);
        
    };
    content_field = document.querySelector('#content_field');
    document.querySelector('#content_field').onkeyup = () => {
        activate_submit();
    }
    document.querySelector('.close').onclick = () => {
        // remove div
        div.remove()
        // remove event listener from button
//        var old_element = document.querySelector('.close')
//        var new_element = old_element.cloneNode(true);
//        old_element.parentNode.replaceChild(new_element, old_element);
        $(".close").off()
    };
    
    // append div
    document.querySelector("#modal-body-contents").prepend(div);
    data_div = document.createElement('div');
    data_div.setAttribute('id','submit-root_type');
    data_div.setAttribute('data',"2");
    document.querySelector("#modal-body-contents").prepend(data_div);
    
    
    document.querySelector("modal")
    new_post();
    
}

function activate_submit(){
    
    if (content_field.value.length > 0) {
        post_submit.disabled = false;
    }
    else {
        post_submit.disabled = true;
    }
    
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function update_post(id, content){
    console.log(`${id} new content: ${content}`);
}

async function load_profile(id, username) {
    //infinite_scroll(() => {});
    console.log(id);
    console.log(username);
    div = document.querySelector('#feed');
    div.innerHTML = "";
    document.querySelector('#show-more-posts').style.display = "none";
    document.querySelector('#header-title').innerHTML = `@${username}'s profile`
    counter = 0;
    await load_more_posts_profile(id);
    show_more = document.querySelector('#show-more-posts').cloneNode(true);
    var children_div = document.querySelector('#profile-children')
    if(children_div){
        children_div.append(show_more);
    }
    
    
    document.querySelector('#show-more-posts').onclick = () => {
        load_more_posts_profile(id);
    }
    
}

async function load_following(username) {
    //infinite_scroll(() => {});
    
    document.querySelector('#header-title').innerHTML = `@${username}'s feed`;
    div = document.querySelector('#feed');
    div.innerHTML = "";
    document.querySelector('#show-more-posts').style.display = "block";
    counter = 0;
    await load_more_posts_following();
    document.querySelector('#show-more-posts').onclick = () => {
        load_more_posts_following();
    }
}

async function load_all_posts(){
    document.querySelector('#header-title').innerHTML = `All Posts`;
    div = document.querySelector('#feed');
    div.innerHTML = "";
    document.querySelector('#show-more-posts').style.display = "block";
    counter = 0;
    await load_more_posts_all();
    document.querySelector('#show-more-posts').onclick = () => {
        load_more_posts_all();
    }
}

function load_more_posts_all(){
    load_more_posts(
        // load more
        async () => {await load_posts()},
        //return fetch for more
        async () => {
            console.log(counter);
            console.log(quantity);
            const response = await fetch(`/posts?start=${counter}&count=${quantity}`);
            const result = await response.json();
            return result;
        
        }
                    
                    
    );
}

function load_more_posts_following(){
    load_more_posts(
        // load more
        async () => {await load_posts(undefined,true);},
        //return fetch for more
        async () => {
            console.log(counter);
            console.log(quantity);
            const response = await fetch(`/following?start=${counter}&count=${quantity}`);
            const result = await response.json();
            return result;
        
        }
                    
                    
    );
}

function load_more_posts_profile(id){
    load_more_posts(
        // load more
        async () => {await load_posts(id);},
        //return fetch for more
        async () => {
            console.log(counter);
            console.log(quantity);
            const response = await fetch(`/posts?start=${counter}&count=${quantity}&user=${id}`);
            const result = await response.json();
            return result;
        
        }
                    
                    
    );
}

function load_more_posts_children(id){
    // implement this. for now, post page shows all comments 1 deep.
}

async function load_more_posts(load, moreCheck){
    // when accessed load the extra posts based on the function
    await load();
    // see if there are any results from the next fetch.
    // if so leave button enabled.
    // otherwise disable click on load more posts
    const result =  await moreCheck();
    console.log(result)
    if (result.length == 0){
        noMoreResults();
    }
    
    
}

function noMoreResults(){
    document.querySelector('#show-more-posts').onclick = () => {};
    document.querySelector('#show-more-posts').style.display = "none";
}


// post methods
async function follow(action,id) {
    console.log(`user ${auth_user} to ${action} user ${id}`);
    const csrftoken = getCookie('csrftoken');
    
    fetch('/follow',{
        method: "POST",
        credentials: 'include',
        body: JSON.stringify({
            "action": action,
            "user": id
        }),
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(async function(result) {
        console.log(result);
        console.log("Done follow");
        
        console.log(result.error);
        var users = await get_users();
        var followers_count = users[id].followers.length;
        var following_count = users[id].following.length;
        console.log(users,followers_count,following_count);
        
        if(!result.error){
            console.log(users);
           
            is_following = await is_user_following(auth_user,id)
            follow_button = document.querySelector(`#follow-${id}`);
            follow_button.innerHTML = is_following ? "unfollow" : "follow";
            followers_div = document.querySelector('#followers_count');
            followers_div.innerHTML = `${followers_count}`;
            following_div = document.querySelector('#following_count');
            following_div.innerHTML = `${following_count}`;
            
        }
        
    })
        
}

async function like(action,post_id) {
    console.log(`Like Func: user ${auth_user} to ${action} post ${post_id}`);
    const csrftoken = getCookie('csrftoken');
    
    const response = await fetch('/like',{
        method: "POST",
        credentials: 'include',
        body: JSON.stringify({
            "action": action,
            "post": post_id
        }),
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-CSRFToken': csrftoken
        }
    });
    
    const result = await response.json();
    
    console.log(result);
    if(!result.error){
        // console.log(users);
       
        document.querySelector(`#like-${post_id}`).innerHTML = await does_user_like(post_id) ? "Unlike" : "Like";
        post = await get_post(post_id);
        console.log(post);
//            followers_div = document.querySelector('#followers_count');
//            followers_div.innerHTML = `${followers_count}`;
//            following_div = document.querySelector('#following_count');
//            following_div.innerHTML = `${following_count}`;
        
    }
    
}

async function delete_post(post_id){
    const csrftoken = getCookie('csrftoken');
    
    const response = await fetch('/delete',{
        method: "POST",
        credentials: 'include',
        body: JSON.stringify({
            "post": post_id
        }),
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-CSRFToken': csrftoken
        }
    })
    
    const result = await response.json()
    
    if(!result.error){
        console.log(result.message)
    }
    console.log(result.error)
    return result.error
}

// Get methods
async function get_users() {
    
    const response = await fetch('/users')
    const json = await response.json();
    let data = {};
    
    json.forEach( u => {
        data[u.id] = u;
    });
    
    return data;
    
}

function get_user(id) {
    fetch(`/users/${id}`)
    .then(response => response.json())
    .then(result => {
        temp_users = {}
        result.forEach( u => {
            users[u.id] = u;
        })
        var users = temp_users;
        //console.log(users);
        console.log(users);
        return users;
    });
}

async function get_post(id) {

    
    const response = await fetch(`/post/${id}`);
    const result = await response.json();
    
    if(!result.error){
        return result;
    }
    
    return null;
}

async function get_posts(start,count) {
    
    const response = await fetch(`posts/?start=${start}&count=${count}`)
    const result = await respone.json()
    
    return result
    
}

//https://www.endyourif.com/set-cursor-position-of-textarea-with-javascript/
//function setSelectionRange(input, selectionStart, selectionEnd) {
//  if (input.setSelectionRange) {
//    input.focus();
//    input.setSelectionRange(selectionStart, selectionEnd);
//  }
//  else if (input.createTextRange) {
//    var range = input.createTextRange();
//    range.collapse(true);
//    range.moveEnd('character', selectionEnd);
//    range.moveStart('character', selectionStart);
//    range.select();
//  }
//}
//
//function setCaretToPos (input, pos) {
//   setSelectionRange(input, pos, pos);
//}
